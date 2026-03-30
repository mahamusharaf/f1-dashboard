import asyncio
import fastf1
import datetime
import pandas as pd
from app.services.websocket_service import manager
from app.services.event_analyzer import EventAnalyzer
from app.services.strategy_engine import StrategyEngine
from app.core.database import SessionLocal
from app.core.schemas import LapUpdate, DriverTiming, EventMessage
from app.core.models import EventType
from app.core.circuits import get_circuit_for_session

class RaceOrchestrator:
    def __init__(self):
        self.is_initialized = False
        self.is_active = False
        self.is_finished = False
        self.session_id = None
        self.year = 0
        self.race_round = 0
        self.current_lap = 0
        self.total_laps = 0
        self.session = None
        self.all_laps = None
        self.drivers = []
        self.team_colors = {}
        self.team_logos = {}
        self.pit_counts = {}
        self.current_virtual_time = None
        self.last_message_idx = 0
        self.circuit_info = {"name": "Unknown", "path": ""}
        self.driver_results = {}
        self.driver_total_laps = {}
        self.driver_max_times = {}
        self.analyzer = EventAnalyzer()
        self.strategy = StrategyEngine()
        self.driver_images = {}

    def initialize_race(self, year: int, race_round: int):
        self.year = year
        self.race_round = race_round
        self.session_id = f"{year}_{race_round}_Race"
        
        fastf1.Cache.enable_cache('f1_cache')
        try:
            self.session = fastf1.get_session(year, race_round, 'R')
            self.session.load(telemetry=True, weather=False, messages=True)
        except Exception as e:
            print(f"[Orchestrator] Failed to load session {year} R{race_round}: {e}")
            self.is_initialized = False
            raise ValueError(f"Race data not available for {year} Round {race_round}. This event might not have occurred yet.")
        
        self.all_laps = self.session.laps

        # Safe total_laps extraction
        lap_max = self.all_laps['LapNumber'].dropna().max()
        self.total_laps = int(lap_max) if not pd.isna(lap_max) else 0
        if self.total_laps == 0:
            raise ValueError(f"No lap data found for {year} Round {race_round}.")

        self.drivers = self.session.drivers
        
        # Pre-cache team colors and logos
        results = self.session.results
        for _, row in results.iterrows():
            abbr = row['Abbreviation']
            team_name = row['TeamName']
            
            # Color
            color = row['TeamColor']
            if not color or pd.isna(color):
                if "audi" in team_name.lower():
                    color = "F50117"
                elif "cadillac" in team_name.lower():
                    color = "909090"
                else:
                    color = "FFFFFF"
            self.team_colors[abbr] = f"#{color}"
            
            # Logo URL
            self.team_logos[abbr] = self._get_team_logo_url(team_name)
            
            # Store final status for DNF detection
            self.driver_results[abbr] = row['Status']

            # Safe laps column extraction
            laps_col = 'NumberOfLaps' if 'NumberOfLaps' in row.index else 'Laps'
            laps_val = row[laps_col] if laps_col in row.index and not pd.isna(row[laps_col]) else self.total_laps
            self.driver_total_laps[abbr] = int(laps_val)
            
            # Cache driver image URL from FastF1 metadata
            if 'HeadshotUrl' in row and not pd.isna(row['HeadshotUrl']):
                url = row['HeadshotUrl']
                if '.transform/' in url:
                    url = url.split('.transform/')[0]
                self.driver_images[abbr] = url
            
            # Get max telemetry time for this driver
            try:
                tel = self.all_laps.pick_driver(abbr).get_telemetry()
                if not tel.empty:
                    self.driver_max_times[abbr] = tel['SessionTime'].max()
                else:
                    self.driver_max_times[abbr] = self.all_laps['Time'].max()
            except:
                self.driver_max_times[abbr] = self.all_laps['Time'].max()

        # Initialize pit counts and virtual time
        self.pit_counts = {d: 0 for d in self.drivers}
        
        if self.all_laps.empty or self.all_laps['LapTime'].dropna().empty:
            print("[Orchestrator] Warning: No lap data found for this session.")
            self.current_virtual_time = datetime.timedelta(0)
            self.is_initialized = True
            return

        start_time = self.all_laps['Time'].min() - self.all_laps['LapTime'].dropna().iloc[0]
        self.current_virtual_time = start_time
        self.last_message_idx = 0
        
        self.current_lap = 1
        self.is_initialized = True
        self._generate_circuit_path()
        self.strategy = StrategyEngine()
        self.is_finished = False
        self.last_timing = []
        self.last_events = []

    async def start_stream(self):
        if not self.is_initialized:
            raise ValueError("Race not initialized")
        if self.is_active:
            return
        self.is_active = True
        asyncio.create_task(self._race_loop())

    def pause_stream(self):
        self.is_active = False

    async def _race_loop(self):
        """Background loop - streams real F1 data using a global session clock."""
        try:
            all_laps = self.all_laps
            
            driver_codes = self.session.results['Abbreviation'].tolist()
            
            start_time = all_laps['Time'].min() - all_laps['LapTime'].dropna().iloc[0]
            
            winner_abbr = self.session.results.iloc[0]['Abbreviation']
            winner_laps = all_laps.pick_driver(winner_abbr)
            end_time = winner_laps['Time'].max()
            
            if self.current_virtual_time is None:
                self.current_virtual_time = start_time
            
            time_step = datetime.timedelta(seconds=1)
            
            driver_telemetries = {}
            for driver in driver_codes:
                try:
                    tel = self.session.laps.pick_driver(driver).get_telemetry()
                    if not tel.empty:
                        driver_telemetries[driver] = tel
                except Exception:
                    continue

            try:
                track_length = self.session.laps.pick_fastest().get_telemetry()['Distance'].max()
            except:
                track_length = 5000

            last_lap_completed = {d: 0 for d in driver_codes}
            last_pos = {}
            last_stint = {d: 1 for d in driver_codes}
            
            print(f"[Orchestrator] Starting simulation from {self.current_virtual_time} to {end_time}")

            while self.current_virtual_time <= end_time and self.is_active:
                driver_updates = []
                positions = {}

                for driver_code in driver_codes:
                    point = None
                    if driver_code in driver_telemetries:
                        tel = driver_telemetries[driver_code]
                        mask = tel['SessionTime'] <= self.current_virtual_time
                        if mask.any():
                            point = tel[mask].iloc[-1]
                    
                    driver_laps = all_laps[all_laps['Driver'] == driver_code]
                    current_lap_data = driver_laps[driver_laps['Time'] <= self.current_virtual_time]
                    lap_num = len(current_lap_data) + 1
                    
                    visual_progress = 0.0
                    try:
                        if point is not None and not pd.isna(point.get('Distance')):
                            visual_progress = (point['Distance'] % track_length) / track_length
                        else:
                            lap_start = driver_laps.iloc[lap_num-2]['Time'] if lap_num > 1 else start_time
                            lap_end = driver_laps.iloc[lap_num-1]['Time'] if lap_num <= len(driver_laps) else end_time
                            total_lap_duration = (lap_end - lap_start).total_seconds()
                            current_duration = (self.current_virtual_time - lap_start).total_seconds()
                            visual_progress = min(0.99, max(0.0, current_duration / total_lap_duration))
                    except:
                        visual_progress = 0.5

                    sorting_distance = (lap_num * track_length) + (visual_progress * track_length)

                    driver_updates.append({
                        "driver": driver_code,
                        "total_distance": sorting_distance,
                        "lap": lap_num,
                        "progress": visual_progress,
                        "point": point,
                        "lap_data": driver_laps.iloc[min(lap_num-1, len(driver_laps)-1)]
                    })

                if not driver_updates:
                    self.current_virtual_time += time_step
                    await asyncio.sleep(0.05)
                    continue

                def standing_sort_key(d_info):
                    d_code = d_info['driver']
                    max_t = self.driver_max_times.get(d_code, end_time)
                    res_laps = self.driver_total_laps.get(d_code, self.total_laps)
                    is_past_telemetry = self.current_virtual_time > max_t + datetime.timedelta(seconds=20)
                    is_past_result_laps = d_info['lap'] > res_laps
                    is_active = not ((is_past_telemetry or is_past_result_laps) and d_info['lap'] < self.total_laps)
                    return (is_active, d_info['total_distance'])

                driver_updates.sort(key=standing_sort_key, reverse=True)
                
                leader_dist = driver_updates[0]['total_distance']
                timing = []
                events = []

                for i, d in enumerate(driver_updates):
                    pos = i + 1
                    driver_code = d['driver']
                    lap_data = d['lap_data']
                    
                    raw_color = self.team_colors.get(driver_code, "#FFFFFF")
                    if not raw_color.startswith("#"):
                        raw_color = f"#{raw_color}"
                    
                    max_time = self.driver_max_times.get(driver_code, end_time)
                    result_laps = self.driver_total_laps.get(driver_code, self.total_laps)
                    is_past_telemetry = self.current_virtual_time > max_time + datetime.timedelta(seconds=20)
                    is_past_result_laps = d['lap'] > result_laps
                    
                    status = "Running"
                    if (is_past_telemetry or is_past_result_laps) and d['lap'] < self.total_laps:
                        status = self.driver_results.get(driver_code, "DNF")
                        if "Finished" in status or "Lap" in status:
                            status = "Running"
                    elif d['lap'] >= self.total_laps:
                        status = "Finished"

                    if d['lap'] <= result_laps and self.current_virtual_time <= max_time:
                        status = "Running"

                    if (status == "Running" or status == "Finished") and d.get('point') is not None:
                        if not pd.isna(d['point'].get('X')) and not pd.isna(d['point'].get('Y')):
                            positions[driver_code] = {
                                "x": d['point']['X'],
                                "y": d['point']['Y'],
                                "driver": driver_code,
                                "team_color": raw_color
                            }
                    
                    if d['lap'] > last_lap_completed[driver_code]:
                        if d['lap'] <= self.total_laps:
                            if d['lap'] > 1:
                                events.append(EventMessage(
                                    event_type=EventType.LAP_START,
                                    message=f"{driver_code} starts lap {d['lap']}.",
                                    lap=d['lap'],
                                    timestamp=datetime.datetime.utcnow().isoformat()
                                ))
                            else:
                                events.append(EventMessage(
                                    event_type=EventType.RACE_START,
                                    message="Lights out and away we go!",
                                    lap=1
                                ))
                        elif d['lap'] == self.total_laps + 1 and status == "Finished":
                            events.append(EventMessage(
                                event_type=EventType.CHECKERED_FLAG,
                                message=f"{driver_code} has crossed the finish line!",
                                lap=self.total_laps
                            ))
                        last_lap_completed[driver_code] = d['lap']

                    if driver_code in last_pos and pos < last_pos[driver_code]:
                        events.append(EventMessage(
                            event_type=EventType.OVERTAKE,
                            message=f"{driver_code} has moved up to P{pos}!",
                            driver=driver_code,
                            lap=d['lap']
                        ))
                    last_pos[driver_code] = pos

                    current_stint = int(lap_data['Stint']) if not pd.isna(lap_data['Stint']) else 1
                    if current_stint > last_stint[driver_code]:
                        events.append(EventMessage(
                            event_type=EventType.PIT_STOP,
                            message=f"{driver_code} has pitted! Fresh set of {lap_data['Compound']} tires fitted.",
                            driver=driver_code,
                            lap=d['lap']
                        ))
                        self.pit_counts[driver_code] = current_stint - 1
                        last_stint[driver_code] = current_stint

                    timing.append(DriverTiming(
                        driver=driver_code,
                        position=pos,
                        lap_time=lap_data['LapTime'].total_seconds() if not pd.isna(lap_data['LapTime']) else 0.0,
                        gap_to_leader=round((leader_dist - d['total_distance']) / 80.0, 3) if i > 0 else 0.0,
                        interval_ahead=0.0,
                        tire_compound=str(lap_data['Compound']) if not pd.isna(lap_data['Compound']) else "UNKNOWN",
                        tire_age=int(lap_data['TyreLife']) if not pd.isna(lap_data['TyreLife']) else 0,
                        pit_stops=self.pit_counts.get(driver_code, 0),
                        team_color=raw_color,
                        team_logo_url=self.team_logos.get(driver_code, ""),
                        driver_image_url=self._get_driver_image_url(driver_code),
                        status=status,
                        lap_progress=round(d['progress'], 3)
                    ))

                self.last_timing = timing
                self.last_events.extend(events)
                if len(self.last_events) > 100:
                    self.last_events = self.last_events[-100:]

                self.current_lap = min(driver_updates[0]['lap'], self.total_laps)
                
                all_done = True
                for t in timing:
                    if t.status == "Running":
                        all_done = False
                        break
                
                if all_done and len(timing) > 0:
                    self.is_finished = True
                    self.is_active = False
                
                if hasattr(self.session, 'messages') and not self.session.messages.empty:
                    new_messages = self.session.messages[
                        (self.session.messages['Time'] > self.current_virtual_time - time_step) & 
                        (self.session.messages['Time'] <= self.current_virtual_time)
                    ]
                    for _, msg in new_messages.iterrows():
                        events.append(EventMessage(
                            event_type=EventType.RADIO_MESSAGE,
                            message=f"RADIO: {msg['Message']}",
                            driver=msg['Driver'],
                            lap=self.current_lap
                        ))
                
                update = LapUpdate(
                    lap_number=self.current_lap,
                    events=events,
                    timing=timing,
                    positions=positions,
                    circuit_path=self.circuit_info["path"],
                    summary={
                        "leader": timing[0].driver if timing else "N/A", 
                        "circuit_name": self.circuit_info.get("name", "Unknown"),
                        "is_active": self.is_active,
                        "is_finished": self.is_finished,
                        "total_laps": self.total_laps,
                        "winner": timing[0].driver if self.is_finished and timing else None
                    }
                )

                await manager.broadcast(update.model_dump_json())
                
                self.current_virtual_time += time_step
                await asyncio.sleep(0.2)

        except Exception as e:
            print(f"[Orchestrator] Error in race loop: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.is_active = False
            try:
                final_events = []
                if self.is_finished:
                    winner_name = self.last_timing[0].driver if self.last_timing else "N/A"
                    final_events.append(EventMessage(
                        event_type=EventType.RACE_END,
                        message=f"CHECKERED FLAG! {winner_name} wins the {self.circuit_info.get('name')}!",
                        driver=winner_name,
                        lap=self.total_laps
                    ))

                final_update = LapUpdate(
                    lap_number=self.current_lap,
                    events=final_events,
                    timing=self.last_timing, 
                    positions={},
                    circuit_path=self.circuit_info["path"],
                    summary={
                        "leader": self.last_timing[0].driver if self.last_timing else "N/A", 
                        "circuit_name": self.circuit_info.get("name", "Unknown"),
                        "is_active": False,
                        "is_finished": self.is_finished,
                        "total_laps": self.total_laps,
                        "winner": self.last_timing[0].driver if self.is_finished and self.last_timing else None
                    }
                )
                await manager.broadcast(final_update.model_dump_json())
            except:
                pass
            print("[Orchestrator] Race loop ended.")

    def _generate_circuit_path(self):
        """Generates a high-fidelity SVG path from the fastest lap's telemetry."""
        try:
            fastest_lap = self.all_laps.pick_fastest()
            tel = fastest_lap.get_telemetry()
            
            x_min, x_max = tel.X.min(), tel.X.max()
            y_min, y_max = tel.Y.min(), tel.Y.max()
            
            width = x_max - x_min
            height = y_max - y_min
            scale = 320 / max(width, height)
            
            x_offset = (400 - width * scale) / 2
            y_offset = (400 - height * scale) / 2
            
            path_points = []
            for i in range(0, len(tel), 2):
                x = (tel.X.iloc[i] - x_min) * scale + x_offset
                y = (tel.Y.iloc[i] - y_min) * scale + y_offset
                path_points.append(f"{x:.1f} {y:.1f}")
            
            path_str = f"M {path_points[0]} L " + " L ".join(path_points[1:]) + " Z"
            self.circuit_info = {
                "name": self.session.event['EventName'],
                "path": path_str
            }
            print(f"[Orchestrator] Generated real circuit path for {self.circuit_info['name']} with {len(path_points)} points")
        except Exception as e:
            print(f"[Orchestrator] Error generating circuit path: {e}")
            from app.core.circuits import get_circuit_for_session
            self.circuit_info = get_circuit_for_session(self.year, self.race_round)

    def _get_team_logo_url(self, team_name: str) -> str:
        mapping = {
            "Mercedes": "https://r2.thesportsdb.com/images/media/team/badge/6caw0r1744037679.png",
            "Ferrari": "https://r2.thesportsdb.com/images/media/team/badge/rxwsqv1420417429.png",
            "Red Bull": "https://r2.thesportsdb.com/images/media/team/badge/nhlev81679826274.png",
            "McLaren": "https://r2.thesportsdb.com/images/media/team/badge/kzqi7v1743602056.png",
            "Alpine": "https://r2.thesportsdb.com/images/media/team/badge/ozhoj31740774899.png",
            "Aston Martin": "https://r2.thesportsdb.com/images/media/team/badge/ez5rlk1740774066.png",
            "Haas": "https://r2.thesportsdb.com/images/media/team/badge/9yp3s51740773680.png",
            "AlphaTauri": "https://r2.thesportsdb.com/images/media/team/badge/ot7pjx1740775883.png",
            "Alpha Tauri": "https://r2.thesportsdb.com/images/media/team/badge/ot7pjx1740775883.png",
            "Alfa Romeo": "https://r2.thesportsdb.com/images/media/team/badge/oyvepw1744380153.png",
            "Williams": "https://r2.thesportsdb.com/images/media/team/badge/fp1cil1740776050.png",
            "Sauber": "https://r2.thesportsdb.com/images/media/team/badge/oyvepw1744380153.png",
            "Racing Bulls": "https://r2.thesportsdb.com/images/media/team/badge/ot7pjx1740775883.png"
        }
        
        url = ""
        team_name_lower = team_name.lower()
        
        if "audi" in team_name_lower:
            url = "https://cdn.simpleicons.org/audi/FFFFFF"
        elif "cadillac" in team_name_lower:
            url = "https://cdn.simpleicons.org/cadillac/FFFFFF"
        elif "stake" in team_name_lower or "kick" in team_name_lower:
            url = "https://r2.thesportsdb.com/images/media/team/badge/oyvepw1744380153.png"
        elif "visa" in team_name_lower or "cash" in team_name_lower or "vcarb" in team_name_lower:
            url = "https://r2.thesportsdb.com/images/media/team/badge/ot7pjx1740775883.png"
            
        if not url:
            for key, val in mapping.items():
                if key.lower() in team_name_lower:
                    url = val
                    break
        
        if not url:
            url = f"https://media.formula1.com/content/dam/fom-website/teams/{self.year}/generic.png"
             
        return url

    def _get_driver_image_url(self, driver_code: str) -> str:
        if driver_code == "LIN":
            return "/lin.png"

        if driver_code in self.driver_images:
            return self.driver_images[driver_code]
            
        slugs = {
            "VER": "max-verstappen", "PER": "sergio-perez", "HAM": "lewis-hamilton",
            "RUS": "george-russell", "LEC": "charles-leclerc", "SAI": "carlos-sainz",
            "NOR": "lando-norris", "PIA": "oscar-piastri", "ALO": "fernando-alonso",
            "STR": "lance-stroll", "GAS": "pierre-gasly", "OCO": "esteban-ocon",
            "ALB": "alexander-albon", "SAR": "logan-sargeant", "TSU": "yuki-tsunoda",
            "RIC": "daniel-ricciardo", "BOT": "valtteri-bottas", "ZHO": "guanyu-zhou",
            "MAG": "kevin-magnussen", "HUL": "nico-hulkenberg", "BEA": "oliver-bearman",
            "LAW": "liam-lawson", "ANT": "andrea-kimi-antonelli", "HAD": "isack-hadjar",
            "MAL": "gabriel-bortoleto", "DOO": "jack-doohan", "POU": "theo-pourchaire"
        }
        
        slug = slugs.get(driver_code)
        if not slug:
            return "https://media.formula1.com/content/dam/fom-website/drivers/generic.jpg"
            
        img_year = self.year
        if img_year >= 2026:
            img_year = 2025
            
        return f"https://media.formula1.com/content/dam/fom-website/drivers/{img_year}Drivers/{slug}.jpg"

orchestrator = RaceOrchestrator()
