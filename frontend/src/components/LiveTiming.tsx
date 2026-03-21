import React from 'react';
import type { DriverTiming } from '../types';

interface Props {
  data: DriverTiming[];
  onDriverSelect: (driver: DriverTiming) => void;
  variant?: 'full' | 'mini';
}

const LiveTiming: React.FC<Props> = ({ data, onDriverSelect, variant = 'full' }) => {
  // Sort by position
  const standings = [...data].sort((a, b) => a.position - b.position);

  const isMini = variant === 'mini';

  const formatTime = (seconds: number) => {
    if (!seconds) return '--:--.---';
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 1000);
    return `${m}:${s.toString().padStart(2, '0')}.${ms.toString().padStart(3, '0')}`;
  };

  const getTireColor = (compound: string) => {
    switch(compound.toUpperCase()) {
      case 'SOFT': return 'text-tire-soft';
      case 'MEDIUM': return 'text-tire-medium';
      case 'HARD': return 'text-tire-hard';
      default: return 'text-f1-light';
    }
  };

  return (
    <div className={`bg-f1-gray/30 rounded-xl ${isMini ? 'p-2' : 'p-4'} shadow-xl border border-white/5 h-full overflow-hidden flex flex-col`}>
      <h2 className={`${isMini ? 'text-sm mb-2' : 'text-xl mb-4'} font-bold flex items-center gap-2 uppercase tracking-tighter`}>
        <span className={`${isMini ? 'w-1 h-4' : 'w-2 h-6'} bg-f1-red rounded-sm`}></span>
        {isMini ? 'Pos' : 'Live Timing'}
      </h2>
      
      <div className="flex-1 overflow-y-auto pr-2 scrollbar-hide">
        {!isMini && (
          <div className="grid grid-cols-12 gap-1 sm:gap-2 text-[10px] sm:text-sm text-f1-light/50 pb-2 border-b border-white/10 mb-2 px-2 uppercase font-black tracking-widest">
            <div className="col-span-1">#</div>
            <div className="col-span-4 sm:col-span-3">Driver</div>
            <div className="col-span-3 text-right">Time</div>
            <div className="col-span-2 text-right hidden sm:block">Gap</div>
            <div className="col-span-2 text-center">Tire</div>
          </div>
        )}

        <div className="flex flex-col gap-1.5 sm:gap-2.5">
          {standings.map((driver) => (
            <div 
              key={driver.driver}
              onClick={() => onDriverSelect(driver)}
              className={`grid grid-cols-12 gap-1 items-center bg-black/40 hover:bg-black/60 transition-all ${isMini ? 'p-1.5' : 'p-2.5 sm:p-3'} rounded-lg cursor-pointer border border-white/5 hover:border-f1-red/50 active:scale-[0.98]`}
            >
              {/* Position */}
              <div className={`${isMini ? 'col-span-2' : 'col-span-1'} font-mono font-black ${isMini ? 'text-[10px]' : 'text-sm sm:text-xl'}`}>
                {driver.status === "Running" || driver.status === "Finished" ? driver.position : (
                  <span className={`${isMini ? 'text-[7px]' : 'text-[9px] sm:text-xs'} bg-f1-red text-white px-1.5 py-0.5 rounded`}>OUT</span>
                )}
              </div>
              
              {/* Driver Image & Name */}
              <div className={`${isMini ? 'col-span-5' : 'col-span-5 sm:col-span-4'} flex items-center gap-1.5 sm:gap-4 min-w-0`}>
                <div 
                  className={`${isMini ? 'w-4 h-4' : 'w-7 h-7 sm:w-10 sm:h-10'} rounded sm:rounded-xl bg-white/5 flex items-center justify-center p-0.5 sm:p-1.5 overflow-hidden shrink-0`}
                  style={{ borderLeft: `${isMini ? '1px' : '3px'} solid ${driver.team_color}` }}
                >
                  <img src={driver.team_logo_url} alt="" className="max-w-full max-h-full object-contain" />
                </div>
                <span className={`font-black uppercase ${isMini ? 'text-[9px]' : 'text-sm sm:text-lg'} tracking-tighter truncate leading-none`}>{driver.driver}</span>
              </div>

              {/* Lap Time (Shared or Mini-specific) */}
              <div className={`${isMini ? 'col-span-5' : 'col-span-3'} text-right font-mono ${isMini ? 'text-[9px]' : 'text-xs sm:text-base'} font-black text-white/90`}>
                {formatTime(driver.lap_time)}
              </div>

              {!isMini && (
                <>
                  <div className="col-span-2 text-right font-mono text-[10px] sm:text-sm text-f1-light/70 hidden sm:block">
                    {driver.status !== "Running" && driver.status !== "Finished" ? (
                      <span className="text-f1-red font-black text-[10px]">{driver.status.toUpperCase()}</span>
                    ) : (
                      driver.position === 1 ? 'Leader' : `+${driver.gap_to_leader.toFixed(3)}s`
                    )}
                  </div>
                  <div className="col-span-2 sm:col-span-2 flex justify-center items-center gap-1">
                    <div className={`text-[10px] sm:text-xs font-black ${getTireColor(driver.tire_compound)}`}>
                      {driver.tire_compound[0]}
                    </div>
                    <div className="text-[8px] sm:text-[10px] font-bold text-f1-light/30">L{driver.tire_age}</div>
                  </div>
                </>
              )}
            </div>
          ))}
          {standings.length === 0 && (
            <div className={`text-center py-4 text-white/40 ${isMini ? 'text-[10px]' : 'text-sm'}`}>Waiting...</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveTiming;
