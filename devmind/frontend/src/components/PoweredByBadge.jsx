import React, { useState } from 'react';

export default function PoweredByBadge() {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="fixed bottom-3 right-3 z-50 text-[12px] font-sans">
      {expanded ? (
        <div
          style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
          className="bg-white border border-[#E5E7EB] rounded-[6px] p-3 w-72 text-[#111827] space-y-2"
        >
          <div className="flex items-center justify-between pb-1.5 border-b border-[#E5E7EB]">
            <span className="font-semibold text-[#111827]">Multi-Model Architecture</span>
            <button
              onClick={() => setExpanded(false)}
              className="text-[#6B7280] hover:text-[#111827] text-xs font-mono px-1"
            >
              ✕
            </button>
          </div>

          <div className="space-y-1.5 text-[11px] text-[#374151]">
            <div>
              <span className="font-medium text-[#111827]">Groq (Llama 3.3 70B):</span> fix, tests, docs
            </div>
            <div>
              <span className="font-medium text-[#111827]">CodeBERT:</span> language detection
            </div>
            <div>
              <span className="font-medium text-[#111827]">StarCoder2:</span> code understanding
            </div>
            <div className="pt-1 border-t border-[#E5E7EB]">
              <a
                href="https://github.com/karak/karak-claude-plugin"
                target="_blank"
                rel="noreferrer"
                className="text-[#2563EB] hover:underline font-medium"
              >
                karak-claude-plugin
              </a>
              <span className="text-[#6B7280]"> — engineering + architecture skills</span>
            </div>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setExpanded(true)}
          style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}
          className="bg-white border border-[#E5E7EB] text-[#6B7280] hover:text-[#111827] hover:border-[#D1D5DB] rounded-[6px] px-2.5 py-1.5 transition-colors cursor-pointer text-[12px]"
        >
          Built with Groq + HuggingFace
        </button>
      )}
    </div>
  );
}
