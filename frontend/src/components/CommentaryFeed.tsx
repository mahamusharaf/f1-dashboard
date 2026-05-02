import React, { useEffect, useRef } from 'react';
import { EventType } from '../types';
import type { EventMessage, EventTypeName } from '../types';

interface Props {
  events: EventMessage[];
}

const CommentaryFeed: React.FC<Props> = ({ events }) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  const getEventStyle = (type: EventTypeName) => {
    switch(type) {
      case EventType.RACE_START:
      case EventType.RACE_END:
        return 'border-l-4 border-f1-red bg-f1-red/10';
      case EventType.OVERTAKE:
        return 'border-l-4 border-blue-500 bg-blue-500/10';
      case EventType.FASTEST_LAP:
        return 'border-l-4 border-purple-500 bg-purple-500/10 text-purple-200';
      case EventType.PIT_STOP:
        return 'border-l-4 border-yellow-500 bg-yellow-500/10';
      case EventType.RADIO_MESSAGE:
        return 'border-l-4 border-green-500 bg-green-500/10 text-green-100';
      default:
        return 'bg-white/5 border-l-4 border-white/10';
    }
  };

  const getEventIcon = (type: EventTypeName) => {
    switch(type) {
      case EventType.RACE_START: return '🚦';
      case EventType.RACE_END: return '🏁';
      case EventType.OVERTAKE: return '⚡';
      case EventType.FASTEST_LAP: return '⏱️';
      case EventType.PIT_STOP: return '⛽';
      case EventType.RADIO_MESSAGE: return '📻';
      default: return '💬';
    }
  };

  return (
    <div className="bg-f1-gray/30 rounded-xl p-3 sm:p-4 shadow-xl border border-white/5 flex flex-col h-full">
      <h2 className="text-lg sm:text-xl font-bold mb-2 sm:mb-4 flex items-center gap-2 uppercase tracking-tighter">
        <span className="w-1.5 sm:w-2 h-5 sm:h-6 bg-f1-red rounded-sm"></span>
        Live Commentary
      </h2>
      
      <div ref={scrollRef} className="flex-1 overflow-y-auto pr-2 space-y-2 scrollbar-hide max-h-[260px] lg:max-h-none">
        {events.length === 0 ? (
          <div className="text-center py-8 text-white/40 italic">Awaiting session...</div>
        ) : (
          events.map((event, idx) => (
            <div 
              key={idx} 
              className={`p-2 rounded pointer-events-auto ${getEventStyle(event.event_type)} transition-all border border-white/5`}
            >
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-base">{getEventIcon(event.event_type)}</span>
                <span className="text-[10px] font-mono text-f1-light/50 bg-black/40 px-1.5 py-0.5 rounded border border-white/5">
                  L{event.lap}
                </span>
                {event.driver && (
                  <span className="text-[11px] font-black uppercase tracking-wider text-f1-light truncate max-w-[80px]">
                    {event.driver}
                  </span>
                )}
                <span className="text-[10px] text-f1-light/30 ml-auto font-mono">
                  {new Date(event.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </span>
              </div>
              <p className="text-[13px] text-f1-light/90 leading-snug">
                {event.message}
              </p>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default CommentaryFeed;
