import React, { useState } from 'react';

const STEPS = [
  { n: 1, title: 'Input Code', text: 'You paste your code and optional language hint.' },
  { n: 2, title: 'CodeBERT Classification', text: 'Classifies the language and problem type.' },
  { n: 3, title: 'StarCoder2 Understanding', text: 'Summarizes what the code is trying to do.' },
  { n: 4, title: 'Groq Llama 3.3 70B Fix & Explanation', text: 'Analyzes context, pinpoints root cause, and applies fix.' },
  { n: 5, title: 'Groq Llama 3.3 70B Unit Tests', text: 'Generates language-idiomatic unit test suites.' },
  { n: 6, title: 'Groq Llama 3.3 70B Documentation', text: 'Enriches code with docstrings and inline comments.' },
  { n: 7, title: 'Complete Results', text: 'Everything streamed directly into the results panel.' },
];

export default function HowItWorks() {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-[#E5E7EB] rounded-[8px] bg-white overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 bg-white text-left hover:bg-[#F9FAFB] transition-colors cursor-pointer"
      >
        <span className="text-xs font-semibold text-[#111827]">
          How It Works
        </span>
        <span className="text-xs text-[#2563EB] font-medium">
          {open ? 'Hide details' : 'View pipeline overview'}
        </span>
      </button>

      {open && (
        <div className="p-4 border-t border-[#E5E7EB] bg-[#F9FAFB] space-y-4">
          {/* Visual SVG / CSS Pipeline Diagram */}
          <div className="p-3 bg-white border border-[#E5E7EB] rounded-[6px] overflow-x-auto">
            <div className="flex items-center space-x-2 text-xs font-mono min-w-[580px]">
              <span className="px-2.5 py-1 bg-[#F3F4F6] border border-[#E5E7EB] rounded-[4px] text-[#111827]">Code Input</span>
              <span className="text-[#9CA3AF]">→</span>
              <span className="px-2.5 py-1 bg-[#EFF6FF] border border-[#BFDBFE] rounded-[4px] text-[#2563EB]">CodeBERT</span>
              <span className="text-[#9CA3AF]">→</span>
              <span className="px-2.5 py-1 bg-[#EFF6FF] border border-[#BFDBFE] rounded-[4px] text-[#2563EB]">StarCoder2</span>
              <span className="text-[#9CA3AF]">→</span>
              <span className="px-2.5 py-1 bg-[#F0FDF4] border border-[#BBF7D0] rounded-[4px] text-[#16A34A]">Groq Fix</span>
              <span className="text-[#9CA3AF]">→</span>
              <span className="px-2.5 py-1 bg-[#F0FDF4] border border-[#BBF7D0] rounded-[4px] text-[#16A34A]">Groq Tests</span>
              <span className="text-[#9CA3AF]">→</span>
              <span className="px-2.5 py-1 bg-[#F0FDF4] border border-[#BBF7D0] rounded-[4px] text-[#16A34A]">Groq Docs</span>
            </div>
          </div>

          {/* 7-Step List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
            {STEPS.map((s) => (
              <div key={s.n} className="flex items-start space-x-2 p-2 bg-white border border-[#E5E7EB] rounded-[6px]">
                <span className="font-mono text-[#2563EB] font-semibold w-4 flex-shrink-0">{s.n}.</span>
                <div>
                  <div className="font-medium text-[#111827]">{s.title}</div>
                  <div className="text-[#6B7280] text-[11px] leading-snug">{s.text}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Karak Credit */}
          <div className="text-[11px] text-[#6B7280] pt-1">
            Build engineered using <a href="https://github.com/karak/karak-claude-plugin" target="_blank" rel="noreferrer" className="text-[#2563EB] hover:underline font-medium">karak-claude-plugin</a> architecture and engineering skills.
          </div>
        </div>
      )}
    </div>
  );
}
