import React, { useEffect, useState } from 'react';
import LiveTiming from './components/LiveTiming';
import CommentaryFeed from './components/CommentaryFeed';
import TrackMap from './components/TrackMap';
import DriverDetailsCard from './components/DriverDetailsCard';
import { useRaceStream } from './hooks/useRaceStream';
import type { DriverTiming } from './types';

const App: React.FC = () => {
  const { raceState, setRaceState, connect, disconnect, clearState } = useRaceStream();
  const [raceInitialized, setRaceInitialized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [selectedDriverCode, setSelectedDriverCode] = useState<string | null>(null);
  const selectedDriver = selectedDriverCode 
    ? raceState.leaderboard.find(d => d.driver === selectedDriverCode) ?? null
    : null;
  const [year, setYear] = useState(2024);
  const [round, setRound] = useState(1);
  const [schedule, setSchedule] = useState<any[]>([]);

  useEffect(() => {
    fetchSchedule();
    connect();
    return () => disconnect();
  }, []);

  const fetchSchedule = async () => {
    try {
      const res = await fetch(`/api/races/schedule?year=${year}`);
      if (res.ok) {
        const data = await res.json();
        setSchedule(data.races);
        if (data.races.length > 0) {
           setRound(data.races[0].round);
        }
      }
    } catch (err) {
      console.error('Failed to fetch schedule', err);
    }
  };

  useEffect(() => {
    fetchSchedule();
  }, [year]);

  const loadRace = async () => {
    setLoading(true);
    setStatusMsg(`Initializing ${year} R${round}...`);
    try {
      const res = await fetch(`/api/races/load?year=${year}&race_round=${round}`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        clearState(); // Clear stale data
        setRaceState(prev => ({ ...prev, totalLaps: data.total_laps }));
        setRaceInitialized(true);
        setStatusMsg('Race ready! Click Start Stream.');
      } else {
        const errData = await res.json().catch(() => ({}));
        setStatusMsg(errData.detail || `Error: ${res.status}`);
        setRaceInitialized(false);
      }
    } catch (err) {
      setStatusMsg('Error connecting to backend');
      console.error(err);
    }
    setLoading(false);
  };

  const startStream = async () => {
    const isResuming = raceState.events.length > 0 || raceState.leaderboard.length > 0;
    setStatusMsg(isResuming ? 'Resuming stream...' : 'Starting stream...');
    try {
      const res = await fetch('/api/stream/start', { method: 'POST' });
      if (res.ok) {
        setStatusMsg(isResuming ? 'Stream resumed!' : 'Stream started!');
      } else {
        const body = await res.json().catch(() => ({ message: res.statusText }));
        setStatusMsg('Error: ' + (body.message ?? res.status));
      }
    } catch (err) {
      setStatusMsg('Error: could not reach backend');
      console.error(err);
    }
  };

  return (
    <div className="h-screen overflow-hidden bg-f1-dark text-f1-light flex flex-col p-2 sm:p-4 md:p-6 w-full">
      {/* Header */}
      <header className="flex flex-col lg:flex-row justify-between items-center mb-6 gap-4 shrink-0 bg-white/5 p-4 rounded-xl border border-white/10">
        <div className="flex flex-col items-center lg:items-start text-center lg:text-left">
          <div className="flex items-center gap-2">
            <img src="/f1-logo.png" alt="F1 Logo" className="h-6 sm:h-8 w-auto brightness-200 mix-blend-screen contrast-125" />
            <span className="text-xl sm:text-2xl font-bold italic tracking-tighter uppercase text-white/90">Live</span>
          </div>
          <p className="text-white/40 text-[10px] sm:text-xs uppercase tracking-widest font-black">Dashboard</p>
        </div>

        <div className="flex flex-wrap justify-center items-center gap-3 sm:gap-4">
          <div className="flex items-center gap-2 bg-black/40 p-1.5 rounded-lg border border-white/10">
             <select 
               value={year} 
               onChange={(e) => setYear(parseInt(e.target.value))}
               className="bg-transparent text-xs sm:text-sm font-bold outline-none border-none cursor-pointer p-1"
             >
               {[2026, 2025, 2024, 2023, 2022, 2021, 2020].map(y => (
                 <option key={y} value={y} className="bg-f1-dark">{y}</option>
               ))}
             </select>
             <div className="w-[1px] h-4 bg-white/10" />
             <select 
               value={round} 
               onChange={(e) => setRound(parseInt(e.target.value))}
               className="bg-transparent text-xs sm:text-sm font-bold outline-none border-none cursor-pointer p-1 max-w-[150px] sm:max-w-none truncate"
             >
               {schedule.map(r => (
                 <option key={r.round} value={r.round} className="bg-f1-dark">
                   R{r.round}: {r.name}
                 </option>
               ))}
             </select>
          </div>

          <div className="flex items-center gap-2">
             {statusMsg && (
               <div className="flex items-center gap-2 bg-f1-red/10 px-3 py-1.5 rounded-full border border-f1-red/20 animate-pulse">
                 <div className={`w-1.5 h-1.5 rounded-full ${statusMsg.includes('Error') ? 'bg-f1-red shadow-[0_0_8px_rgba(255,24,1,0.6)]' : 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]'}`} />
                 <span className="text-[10px] font-black text-f1-red uppercase tracking-wider whitespace-nowrap">{statusMsg}</span>
               </div>
             )}
             
             {raceState.totalLaps > 0 && (
               <div className="flex items-center gap-2 bg-f1-red/10 px-3 py-1.5 rounded-lg border border-f1-red/20">
                 <span className="text-[10px] uppercase font-black tracking-widest text-f1-red">Lap</span>
                 <span className="font-mono text-sm font-black">
                   <span className="text-white">{raceState.currentLap}</span> 
                   <span className="text-white/20 mx-1">/</span>
                   <span className="text-white/60">{raceState.totalLaps}</span>
                 </span>
               </div>
             )}
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={loadRace}
              disabled={loading}
              className="px-3 sm:px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs sm:text-sm font-bold transition-all disabled:opacity-50 border border-white/5 active:scale-95"
            >
              {loading ? '...' : raceInitialized ? 'Reset' : 'Initialize'}
            </button>
            <button
              onClick={startStream}
              disabled={!raceInitialized || raceState.isStreamActive}
              className="px-4 sm:px-6 py-2 bg-f1-red text-white hover:bg-red-700 rounded-lg text-xs sm:text-sm font-black transition-all shadow-lg shadow-f1-red/20 disabled:opacity-50 active:scale-95"
            >
              {raceState.events.length > 0 && !raceState.isStreamActive ? 'Resume' : 'Start'}
            </button>
            <button
              onClick={async (e) => {
                e.stopPropagation();
                await fetch('/api/stream/pause', { method: 'POST' });
                setRaceState(prev => ({ ...prev, isStreamActive: false }));
                setStatusMsg('Stream paused');
              }}
              disabled={!raceState.isStreamActive}
              className="p-2 sm:px-4 py-2 bg-white/5 hover:bg-white/10 rounded-lg text-xs sm:text-sm font-bold transition-all disabled:opacity-50 border border-white/5 active:scale-95"
            >
              <span className="hidden sm:inline">Pause</span>
              <span className="sm:hidden">||</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <div className="flex-1 flex flex-col lg:grid lg:grid-cols-12 gap-4 h-full min-h-0 lg:overflow-hidden overflow-hidden">

        {/* Desktop Left / Mobile Bottom Row Section (Leaderboard & Card) */}
        {/* On mobile, we only show Mini Timing in the top row, so this full version is lg-only for the left column */}
        <div className="hidden lg:flex lg:col-span-5 h-full flex-col gap-4 min-h-0 overflow-hidden">
          <div className="flex-1 min-h-0">
            <LiveTiming
              data={raceState.leaderboard}
              onDriverSelect={(d) => setSelectedDriverCode(d.driver)}
            />
          </div>
          <div className="h-64 shrink-0">
            <DriverDetailsCard driver={selectedDriver} />
          </div>
        </div>

        {/* Right Column (Desktop) / Main Area (Mobile) */}
        <div className="col-span-12 lg:col-span-7 h-full flex flex-col gap-2 sm:gap-4 min-h-0 overflow-hidden">
          
          {/* Mobile Top Row: Map + Mini Leaderboard */}
          <div className="flex lg:hidden h-[45%] sm:h-[40%] gap-2 shrink-0">
            <div className="flex-[3] bg-f1-gray/20 rounded-xl border border-white/5 relative overflow-hidden">
              <TrackMap 
                circuitPath={raceState.circuitPath}
                positions={raceState.leaderboard
                  .filter(d => d.status === "Running" || d.status === "Finished")
                  .reduce((acc, curr) => ({
                  ...acc,
                  [curr.driver]: { progress: curr.lap_progress, color: curr.team_color }
                }), {})} 
              />
              <div className="absolute top-2 left-2 flex flex-col">
                 <span className="text-[8px] uppercase font-black tracking-tighter text-f1-red">Map</span>
                 <span className="text-[10px] text-f1-light/40 font-medium truncate max-w-[80px]">{raceState.circuitName}</span>
              </div>
            </div>
            <div className="flex-[2] min-w-0">
              <LiveTiming
                variant="mini"
                data={raceState.leaderboard}
                onDriverSelect={(d) => setSelectedDriverCode(d.driver)}
              />
            </div>
          </div>

          {/* Desktop Top Row Map Case */}
          <div className="hidden lg:block h-[350px] shrink-0 bg-f1-gray/20 rounded-xl border border-white/5 relative overflow-hidden group">
            <TrackMap 
              circuitPath={raceState.circuitPath}
              positions={raceState.leaderboard
                .filter(d => d.status === "Running" || d.status === "Finished")
                .reduce((acc, curr) => ({
                ...acc,
                [curr.driver]: { progress: curr.lap_progress, color: curr.team_color }
              }), {})} 
            />
            <div className="absolute top-4 left-4 flex flex-col gap-1">
               <span className="text-[10px] uppercase font-black tracking-tighter text-f1-red">Track Map</span>
               <span className="text-xs text-f1-light/40 font-medium capitalize">{raceState.circuitName}</span>
            </div>
          </div>

          {/* Commentary (Shared) */}
          <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
            <CommentaryFeed events={raceState.events} />
          </div>
          
          {/* Driver Details (Mobile Only - Small strip) */}
          {selectedDriver && (
            <div className="lg:hidden h-20 shrink-0 animate-slide-in-up">
               <div className="bg-f1-gray/40 backdrop-blur-md rounded-xl p-2 border border-white/10 h-full flex items-center gap-3 shadow-2xl relative">
                  <button 
                    onClick={() => setSelectedDriverCode(null)}
                    className="absolute -top-2 -right-2 w-6 h-6 bg-f1-red text-white flex items-center justify-center rounded-full text-xs font-black shadow-lg"
                  >
                    ×
                  </button>
                  <div className="w-14 h-14 rounded-lg overflow-hidden border border-white/20 shrink-0">
                    <img 
                      src={selectedDriver.driver_image_url} 
                      alt="" 
                      className="w-full h-full object-cover object-top"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src = 'https://media.formula1.com/content/dam/fom-website/drivers/generic.jpg';
                      }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-[10px] text-f1-light/40 uppercase font-black tracking-widest mb-0.5">Selected Driver</p>
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-black uppercase truncate text-white">{selectedDriver.driver}</p>
                      <span className="text-[10px] bg-white/10 px-1 rounded font-bold text-white/60">P{selectedDriver.position}</span>
                    </div>
                    <p className="text-[10px] text-f1-light/50 font-bold uppercase">{selectedDriver.status}</p>
                  </div>
                  <div className="text-right pr-2">
                    <p className="text-xs font-mono font-black text-f1-red leading-none">{selectedDriver.lap_time.toFixed(3)}s</p>
                    <p className="text-[8px] text-white/20 uppercase font-black tracking-tighter mt-1">Last Lap</p>
                  </div>
               </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default App;
