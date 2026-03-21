import React from 'react';
import type { DriverTiming } from '../types';

interface Props {
  driver: DriverTiming | null;
}

const DriverDetailsCard: React.FC<Props> = ({ driver }) => {
  if (!driver) {
    return (
      <div className="bg-f1-gray/30 rounded-xl p-4 shadow-xl border border-white/5 h-full flex items-center justify-center text-white/40">
        Select a driver to view details
      </div>
    );
  }

  const getTireBadge = (compound: string) => {
    const isSoft = compound.toUpperCase() === 'SOFT';
    const isMed = compound.toUpperCase() === 'MEDIUM';
    const isHard = compound.toUpperCase() === 'HARD';
    
    return (
      <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${isSoft ? 'bg-f1-red text-white' : isMed ? 'bg-yellow-500 text-black' : isHard ? 'bg-white text-black' : 'bg-gray-500 text-white'}`}>
        {compound}
      </span>
    );
  };

  return (
    <div className="bg-f1-gray/30 rounded-xl p-4 sm:p-6 shadow-xl border border-white/5 h-full flex flex-col overflow-y-auto scrollbar-hide">
      <div className="flex flex-col sm:flex-row justify-between items-center sm:items-start mb-6 gap-4 relative">
        <div className="text-center sm:text-left">
          <h2 className="text-2xl sm:text-3xl font-black uppercase tracking-wider">{driver.driver}</h2>
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <p className="text-f1-light/60 text-xs sm:text-sm font-bold">P{driver.position}</p>
            {driver.status !== "Running" && driver.status !== "Finished" && (
              <span className="bg-f1-red text-white text-[8px] sm:text-[10px] font-black px-1.5 py-0.5 rounded animate-pulse">
                {driver.status.toUpperCase()}
              </span>
            )}
            {driver.status === "Finished" && (
              <span className="bg-yellow-500 text-black text-[8px] sm:text-[10px] font-black px-1.5 py-0.5 rounded">
                FIN
              </span>
            )}
          </div>
        </div>
        <div className="relative group shrink-0">
          <div className="absolute -top-2 -right-2 w-20 h-20 sm:w-24 sm:h-24 bg-gradient-to-br from-f1-red/20 to-transparent rounded-full blur-2xl opacity-50" />
          <div className="relative w-24 h-24 sm:w-32 sm:h-32 rounded-xl border border-white/10 overflow-hidden shadow-2xl bg-black/40">
            <img 
              src={driver.driver_image_url} 
              alt={driver.driver} 
              className="w-full h-full object-cover object-top scale-110"
              onError={(e) => {
                (e.target as HTMLImageElement).src = 'https://media.formula1.com/content/dam/fom-website/drivers/generic.jpg';
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
            <div className="absolute bottom-1 right-2 text-2xl sm:text-3xl font-black italic text-white/90 drop-shadow-md">
              {driver.status === "Running" || driver.status === "Finished" ? driver.position : "OUT"}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-black/40 p-3 rounded border border-white/5">
          <p className="text-xs text-f1-light/50 uppercase mb-1">Last Lap</p>
          <p className="font-mono text-xl">
            {driver.status === "Running" || driver.status === "Finished" ? `${driver.lap_time.toFixed(3)}s` : "---"}
          </p>
        </div>
        <div className="bg-black/40 p-3 rounded border border-white/5">
          <p className="text-xs text-f1-light/50 uppercase mb-1">Gap to Leader</p>
          <p className="font-mono text-xl">
            {driver.status === "Running" || driver.status === "Finished" ? `+${driver.gap_to_leader.toFixed(3)}s` : driver.status}
          </p>
        </div>
      </div>

      <div className="mt-auto">
        <h3 className="text-sm uppercase text-f1-light/50 font-semibold mb-3 border-b border-white/10 pb-2">Telemetry & Strategy</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between items-center">
             <span className="text-f1-light/70">Tire Compound</span>
             {getTireBadge(driver.tire_compound)}
          </div>
          <div className="flex justify-between items-center">
             <span className="text-f1-light/70">Tire Age</span>
             <span className="font-mono font-bold">{driver.tire_age} Laps</span>
          </div>
          <div className="flex justify-between items-center">
             <span className="text-f1-light/70">Pit Stops</span>
             <span className="font-mono font-bold">{driver.pit_stops}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DriverDetailsCard;
