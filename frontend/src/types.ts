export const EventType = {
  RACE_START: "RACE_START",
  LAP_START: "LAP_START",
  POSITION_CHANGE: "POSITION_CHANGE",
  OVERTAKE: "OVERTAKE",
  PIT_STOP: 'PIT_STOP',
  FASTEST_LAP: 'FASTEST_LAP',
  RADIO_MESSAGE: 'RADIO_MESSAGE',
  STRATEGY: 'STRATEGY',
  AI_COMMENTARY: 'AI_COMMENTARY',
  RACE_END: 'RACE_END',
} as const;

export type EventTypeName = 
  | 'RACE_START' 
  | 'LAP_START' 
  | 'POSITION_CHANGE' 
  | 'OVERTAKE' 
  | 'PIT_STOP' 
  | 'FASTEST_LAP'
  | 'RADIO_MESSAGE'
  | 'STRATEGY' 
  | 'AI_COMMENTARY' 
  | 'RACE_END';

export interface EventMessage {
  event_type: EventTypeName;
  message: string;
  driver?: string;
  lap: number;
  additional_data?: any;
  timestamp: string;
}

export interface DriverTiming {
  driver: string;
  position: number;
  lap_time: number;
  gap_to_leader: number;
  interval_ahead: number;
  tire_compound: string;
  tire_age: number;
  pit_stops: number;
  team_color: string;
  team_logo_url: string;
  driver_image_url: string;
  status: string;
  lap_progress: number;
}

export interface LapUpdate {
  lap_number: number;
  events: EventMessage[];
  timing: DriverTiming[];
  positions: any;
  circuit_path?: string;
  summary: any;
}

// Global UI State
export interface RaceState {
  currentLap: number;
  totalLaps: number;
  isStreamActive: boolean;
  isWsConnected: boolean;
  isFinished: boolean;
  winner?: string | null;
  events: EventMessage[];
  leaderboard: DriverTiming[];
  positions?: any;
  circuitPath?: string;
  circuitName?: string;
}
