import React from 'react';
import type { DriverTiming } from '../types';

interface Props {
  data: DriverTiming[];
  onDriverSelect: (driver: DriverTiming) => void;
  variant?: 'full' | 'mini';
}

const LiveTiming: React.FC<Props> = ({ data, onDriverSelect, variant = 'full' }) => {
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
    switch (compound.toUpperCase()) {
      case 'SOFT': return 'text-tire-soft';
      case 'MEDIUM': return 'text-tire-medium';
      case 'HARD': return 'text-tire-hard';
      default: return 'text-f1-light';
    }
  };

  /* ─────────────────────────────────────────────
     MINI VARIANT — fits in ~145 px on real phones
     Shows only: pos | team colour bar | 3-letter code
     No logo, no lap time to avoid truncation
  ───────────────────────────────────────────── */
  if (isMini) {
    return (
      <div className="bg-f1-gray/30 rounded-xl p-2 shadow-xl border border-white/5 h-full flex flex-col overflow-hidden">
        <h2 className="text-sm mb-2 font-bold flex items-center gap-2 uppercase tracking-tighter">
          <span className="w-1 h-4 bg-f1-red rounded-sm" />
          Pos
        </h2>

        <div className="flex-1 overflow-y-auto scrollbar-hide flex flex-col gap-1">
          {standings.map((driver) => (
            <button
              key={driver.driver}
              onClick={() => onDriverSelect(driver)}
              className="flex items-center gap-1.5 w-full text-left bg-black/40 active:bg-black/70 transition-colors px-1.5 py-[6px] rounded-lg border border-white/5 active:scale-[0.97]"
            >
              {/* Position number */}
              <span className="w-4 shrink-0 text-center text-[10px] font-mono font-black text-white/60 leading-none">
                {driver.status === 'Running' || driver.status === 'Finished'
                  ? driver.position
                  : <span className="text-[7px] bg-f1-red text-white px-0.5 rounded">✕</span>}
              </span>

              {/* Team colour pill */}
              <span
                className="w-[3px] h-3.5 rounded-full shrink-0"
                style={{ backgroundColor: driver.team_color }}
              />

              {/* 3-letter driver code — never truncated */}
              <span className="text-[11px] font-black uppercase tracking-tight text-white leading-none">
                {driver.driver}
              </span>
            </button>
          ))}

          {standings.length === 0 && (
            <div className="text-center py-4 text-white/40 text-[10px]">Waiting...</div>
          )}
        </div>
      </div>
    );
  }

  /* ─────────────────────────────────────────────
     FULL VARIANT — left sidebar on desktop
  ───────────────────────────────────────────── */
  return (
    <div className="bg-f1-gray/30 rounded-xl p-4 shadow-xl border border-white/5 h-full overflow-hidden flex flex-col">
      <h2 className="text-xl mb-4 font-bold flex items-center gap-2 uppercase tracking-tighter">
        <span className="w-2 h-6 bg-f1-red rounded-sm" />
        Live Timing
      </h2>

      <div className="flex-1 overflow-y-auto pr-2 scrollbar-hide">
        {/* Column headers */}
        <div className="grid grid-cols-12 gap-1 text-[10px] sm:text-sm text-f1-light/50 pb-2 border-b border-white/10 mb-2 px-2 uppercase font-black tracking-widest">
          <div className="col-span-1">#</div>
          <div className="col-span-4 sm:col-span-3">Driver</div>
          <div className="col-span-3 text-right">Time</div>
          <div className="col-span-2 text-right hidden sm:block">Gap</div>
          <div className="col-span-2 text-center">Tire</div>
        </div>

        <div className="flex flex-col gap-1.5 sm:gap-2.5">
          {standings.map((driver) => (
            <div
              key={driver.driver}
              onClick={() => onDriverSelect(driver)}
              className="grid grid-cols-12 gap-1 items-center bg-black/40 hover:bg-black/60 transition-all p-2.5 sm:p-3 rounded-lg cursor-pointer border border-white/5 hover:border-f1-red/50 active:scale-[0.98]"
            >
              {/* Position */}
              <div className="col-span-1 font-mono font-black text-sm sm:text-xl">
                {driver.status === 'Running' || driver.status === 'Finished' ? driver.position : (
                  <span className="text-[9px] sm:text-xs bg-f1-red text-white px-1.5 py-0.5 rounded">OUT</span>
                )}
              </div>

              {/* Logo + Name */}
              <div className="col-span-5 sm:col-span-4 flex items-center gap-1.5 sm:gap-4 min-w-0">
                <div
                  className="w-7 h-7 sm:w-10 sm:h-10 rounded sm:rounded-xl bg-white/5 flex items-center justify-center p-0.5 sm:p-1.5 overflow-hidden shrink-0"
                  style={{ borderLeft: `3px solid ${driver.team_color}` }}
                >
                  <img src={driver.team_logo_url} alt="" className="max-w-full max-h-full object-contain" />
                </div>
                <span className="font-black uppercase text-sm sm:text-lg tracking-tighter truncate leading-none">
                  {driver.driver}
                </span>
              </div>

              {/* Lap Time */}
              <div className="col-span-3 text-right font-mono text-xs sm:text-base font-black text-white/90">
                {formatTime(driver.lap_time)}
              </div>

              {/* Gap — desktop only */}
              <div className="col-span-2 text-right font-mono text-[10px] sm:text-sm text-f1-light/70 hidden sm:block">
                {driver.status !== 'Running' && driver.status !== 'Finished' ? (
                  <span className="text-f1-red font-black text-[10px]">{driver.status.toUpperCase()}</span>
                ) : (
                  driver.position === 1 ? 'Leader' : `+${driver.gap_to_leader.toFixed(3)}s`
                )}
              </div>

              {/* Tire */}
              <div className="col-span-2 flex justify-center items-center gap-1">
                <div className={`text-[10px] sm:text-xs font-black ${getTireColor(driver.tire_compound)}`}>
                  {driver.tire_compound[0]}
                </div>
                <div className="text-[8px] sm:text-[10px] font-bold text-f1-light/30">L{driver.tire_age}</div>
              </div>
            </div>
          ))}

          {standings.length === 0 && (
            <div className="text-center py-4 text-white/40 text-sm">Waiting...</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LiveTiming;
