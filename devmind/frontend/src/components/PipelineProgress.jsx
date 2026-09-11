import React from 'react';

const STAGES = [
  { id: 1, label: '1. Classify' },
  { id: 2, label: '2. Understand' },
  { id: 3, label: '3. Fix' },
  { id: 4, label: '4. Tests' },
  { id: 5, label: '5. Docs' },
];

export default function PipelineProgress({ stageStates }) {
  return (
    <div className="flex items-center space-x-2 py-2.5 px-4 bg-white border-b border-[#E5E7EB] overflow-x-auto">
      <span className="text-xs text-[#6B7280] font-medium mr-1 flex-shrink-0">
        Pipeline
      </span>
      <div className="flex items-center space-x-2">
        {STAGES.map((stage) => {
          const state = stageStates[stage.id] || { status: 'idle' };
          const isPending = state.status === 'idle';
          const isRunning = state.status === 'running';
          const isComplete = state.status === 'complete';
          const isFailed = state.status === 'error';

          let chipStyle = 'bg-[#F3F4F6] text-[#6B7280] border-[#E5E7EB]';
          if (isRunning) {
            chipStyle = 'bg-[#EFF6FF] text-[#2563EB] border-[#BFDBFE]';
          } else if (isComplete) {
            chipStyle = 'bg-[#F0FDF4] text-[#16A34A] border-[#BBF7D0]';
          } else if (isFailed) {
            chipStyle = 'bg-[#FEF2F2] text-[#DC2626] border-[#FECACA]';
          }

          return (
            <div
              key={stage.id}
              className={`inline-flex items-center space-x-1.5 px-2.5 py-1 text-xs font-mono rounded-[6px] border transition-colors duration-200 ease-in-out whitespace-nowrap ${chipStyle}`}
            >
              {isRunning && (
                <svg className="w-3 h-3 animate-spin text-[#2563EB]" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path>
                </svg>
              )}
              {isComplete && (
                <svg className="w-3 h-3 text-[#16A34A]" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              )}
              {isPending && (
                <span className="w-1.5 h-1.5 rounded-full bg-[#9CA3AF]"></span>
              )}
              {isFailed && (
                <span className="w-1.5 h-1.5 rounded-full bg-[#DC2626]"></span>
              )}
              <span>{stage.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
