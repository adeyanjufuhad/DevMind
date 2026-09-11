import React, { useState, useEffect, useRef } from 'react';
import { SAMPLE_SNIPPETS } from './snippets';

export default function CodeEditor({
  code,
  onChange,
  onAnalyze,
  isLoading,
  onSelectSample,
  detectedLanguage,
}) {
  const [isEditing, setIsEditing] = useState(true);
  const textareaRef = useRef(null);
  const lineCount = code ? code.split('\n').length : 1;
  const lineNumbers = Array.from({ length: Math.max(lineCount, 22) }, (_, i) => i + 1);

  // Automatically show highlighted view once Stage 1 detects language
  useEffect(() => {
    setIsEditing(!detectedLanguage || isLoading);
  }, [detectedLanguage, isLoading]);

  const getHighlightedHtml = () => {
    if (!code || !detectedLanguage || typeof window === 'undefined' || !window.hljs) return null;
    try {
      const lang = window.hljs.getLanguage(detectedLanguage) ? detectedLanguage : 'plaintext';
      return window.hljs.highlight(code, { language: lang, ignoreIllegals: true }).value;
    } catch {
      return null;
    }
  };

  const highlightedHtml = !isEditing && detectedLanguage ? getHighlightedHtml() : null;

  const handleStartEdit = () => {
    setIsEditing(true);
    setTimeout(() => textareaRef.current?.focus(), 20);
  };

  return (
    <div className="flex flex-col h-full bg-white border border-[#E5E7EB] rounded-[8px] overflow-hidden">
      {/* Editor Toolbar */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-white border-b border-[#E5E7EB]">
        <div className="flex items-center space-x-3">
          <span className="text-xs font-semibold text-[#111827]">Source Code</span>
          <span className="text-xs font-mono text-[#6B7280]">{lineCount} lines</span>
          {detectedLanguage && (
            <span className="px-2 py-0.5 bg-[#EFF6FF] text-[#2563EB] border border-[#BFDBFE] rounded-[4px] font-mono text-[11px]">
              {detectedLanguage}
            </span>
          )}
        </div>

        <div className="flex items-center space-x-2">
          {detectedLanguage && (
            <button
              onClick={() => (isEditing ? setIsEditing(false) : handleStartEdit())}
              className="text-xs text-[#2563EB] hover:text-[#1D4ED8] font-medium px-2 py-1 rounded-[6px] hover:bg-[#F3F4F6] transition-colors"
            >
              {isEditing ? 'View Highlighted' : 'Edit'}
            </button>
          )}

          <select
            onChange={(e) => {
              if (e.target.value && SAMPLE_SNIPPETS[e.target.value]) {
                onSelectSample(SAMPLE_SNIPPETS[e.target.value]);
                setIsEditing(true);
              }
              e.target.value = "";
            }}
            defaultValue=""
            className="bg-[#F3F4F6] text-[#111827] text-xs font-medium rounded-[6px] px-2.5 py-1.5 border border-[#E5E7EB] hover:border-[#D1D5DB] focus:outline-none focus:border-[#2563EB] cursor-pointer"
          >
            <option value="" disabled>Load example snippet...</option>
            <option value="python_fib">Python recursion error</option>
            <option value="js_async">JavaScript async bug</option>
            <option value="python_security">Python SQL injection</option>
          </select>

          {code && (
            <button
              onClick={() => { onChange(''); setIsEditing(true); }}
              disabled={isLoading}
              className="text-xs text-[#6B7280] hover:text-[#DC2626] px-2 py-1 rounded-[6px] hover:bg-[#F3F4F6] transition-colors"
            >
              Clear
            </button>
          )}
        </div>
      </div>

      {/* Editor Surface: white background to match UI theme */}
      <div className="flex flex-1 min-h-[460px] bg-white font-mono text-xs overflow-hidden">
        <div className="select-none py-4 px-3 text-right bg-[#F9FAFB] text-[#8B949E] border-r border-[#E5E7EB] w-12 flex-shrink-0 leading-6">
          {lineNumbers.map((num) => <div key={num}>{num}</div>)}
        </div>

        {highlightedHtml ? (
          <div
            onClick={handleStartEdit}
            title="Click to edit code"
            className="flex-1 w-full py-4 px-4 bg-white text-[#24292e] leading-6 font-mono text-xs code-scroll overflow-y-auto cursor-text whitespace-pre"
          >
            <code
              className={`hljs language-${detectedLanguage}`}
              style={{ background: 'transparent', padding: 0 }}
              dangerouslySetInnerHTML={{ __html: highlightedHtml }}
            />
          </div>
        ) : (
          <textarea
            ref={textareaRef}
            value={code}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Paste broken or problematic code here..."
            disabled={isLoading}
            spellCheck="false"
            className="flex-1 w-full py-4 px-4 bg-white text-[#111827] placeholder-[#9CA3AF] focus:outline-none resize-none leading-6 font-mono text-xs caret-[#2563EB] code-scroll overflow-y-auto"
          />
        )}
      </div>

      {/* Footer Action Bar */}
      <div className="flex items-center justify-between px-4 py-3 bg-white border-t border-[#E5E7EB]">
        <span className="text-xs text-[#6B7280]">
          {detectedLanguage ? `Detected: ${detectedLanguage}` : 'Stage 1 detects language if not specified'}
        </span>

        <button
          onClick={onAnalyze}
          disabled={isLoading || !code.trim()}
          className="inline-flex items-center justify-center px-4 py-2 bg-[#2563EB] hover:bg-[#1D4ED8] disabled:bg-[#93C5FD] text-white text-xs font-medium rounded-[6px] transition-colors cursor-pointer disabled:cursor-not-allowed"
        >
          {isLoading ? 'Running Pipeline...' : 'Run Pipeline'}
        </button>
      </div>
    </div>
  );
}
