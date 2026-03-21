import { useState, useCallback } from 'react';
import type { RaceState, LapUpdate } from '../types';

export function useRaceStream() {
  const [raceState, setRaceState] = useState<RaceState>({
    currentLap: 0,
    totalLaps: 0,
    isStreamActive: false,
    isWsConnected: false,
    events: [],
    leaderboard: [],
    circuitPath: '',
    circuitName: '',
    isFinished: false,
    winner: null
  });

  const [ws, setWs] = useState<WebSocket | null>(null);

  const clearState = useCallback(() => {
    setRaceState({
      currentLap: 0,
      totalLaps: 0,
      isStreamActive: false,
      isWsConnected: false,
      events: [],
      leaderboard: [],
      circuitPath: '',
      circuitName: '',
      isFinished: false,
      winner: null
    });
  }, []);

  const connect = useCallback(() => {
    clearState(); // Clear any stale data from previous races
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/race/live`;
    
    const socket = new WebSocket(wsUrl);

    socket.onopen = () => {
      console.log('Connected to stream');
      setRaceState(prev => ({ ...prev, isWsConnected: true }));
    };

    socket.onmessage = (event) => {
      try {
        const update: LapUpdate = JSON.parse(event.data);
        
        setRaceState(prev => {
           const newEvents = [...prev.events, ...update.events];
           if (newEvents.length > 100) {
             newEvents.splice(0, newEvents.length - 100);
           }

           return {
             ...prev,
             isStreamActive: update.summary?.is_active ?? true, 
             isFinished: update.summary?.is_finished ?? false,
             winner: update.summary?.winner ?? null,
             currentLap: update.lap_number,
             totalLaps: update.summary?.total_laps ?? prev.totalLaps,
             events: newEvents,
             leaderboard: update.timing,
             circuitPath: update.circuit_path ?? prev.circuitPath,
             circuitName: update.summary?.circuit_name ?? prev.circuitName
           };
        });
      } catch (err) {
        console.error('Error parsing WS message:', err);
      }
    };

    socket.onclose = () => {
      console.log('Stream disconnected');
      setRaceState(prev => ({ ...prev, isWsConnected: false, isStreamActive: false }));
    };

    setWs(socket);

    return () => {
      socket.close();
    };
  }, [clearState]);

  const disconnect = useCallback(() => {
    if (ws) {
      ws.close();
      setWs(null);
    }
  }, [ws]);

  return {
    raceState,
    setRaceState,
    connect,
    disconnect,
    clearState
  };
}
