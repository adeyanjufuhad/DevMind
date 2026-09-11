import React, { useState } from 'react';

export default function ResultsTabs({ results, hasResults }) {
  const [activeTab, setActiveTab] = useState('analysis');
  const [copiedKey, setCopiedKey] = useState(null);

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 1500);
  };

  const tabs = [
    { id: 'analysis', label: 'Bug Analysis' },
    { id: 'fix', label: 'Fixed Code' },
    { id: 'tests', label: 'Unit Tests' },
    { id: 'docs', label: 'Documentation' },
  ];

  if (!hasResults) {
    return (
      <div className="flex-1 flex items-center justify-center p-8 bg-white text-xs text-[#6B7280]">
        Pipeline results will appear here.
      </div>
    );
  }

  return (
    <div className="flex flex-col flex-1 bg-white overflow-hidden">
      {/* Minimal Underline-Style Tabs */}
      <div className="flex items-center space-x-6 px-4 border-b border-[#E5E7EB] bg-white">
        {tabs.map((tab) => {
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-3 text-xs font-medium border-b-2 transition-colors cursor-pointer ${
                isActive
                  ? 'border-[#2563EB] text-[#2563EB] font-semibold'
                  : 'border-transparent text-[#6B7280] hover:text-[#111827]'
              }`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Panels */}
      <div className="p-4 flex-1 overflow-y-auto space-y-4">
        {/* Tab 1: Bug Analysis */}
        {activeTab === 'analysis' && (
          <div className="space-y-4 text-xs">
            {/* Classification Metadata */}
            {results.classification && (
              <div className="flex items-center space-x-2">
                <span className="px-2 py-0.5 bg-[#F3F4F6] text-[#111827] rounded-[4px] border border-[#E5E7EB] font-mono">
                  {results.classification.language}
                </span>
                <span className="px-2 py-0.5 bg-[#F3F4F6] text-[#6B7280] rounded-[4px] border border-[#E5E7EB] font-mono">
                  {results.classification.error_type}
                </span>
              </div>
            )}

            {/* Root Cause */}
            <div className="border border-[#E5E7EB] rounded-[6px] p-3.5 bg-white">
              <div className="font-semibold text-[#111827] mb-1">Root Cause</div>
              <p className="text-[#374151] leading-relaxed">
                {results.fix?.root_cause || results.fix?.error || 'Analyzing error...'}
              </p>
            </div>

            {/* Junior Explanation */}
            <div className="border border-[#E5E7EB] rounded-[6px] p-3.5 bg-white">
              <div className="font-semibold text-[#111827] mb-1">Junior Developer Walkthrough</div>
              <p className="text-[#374151] leading-relaxed whitespace-pre-line">
                {results.fix?.explanation || 'Explanation pending...'}
              </p>
            </div>
          </div>
        )}

        {/* Tab 2: Fixed Code */}
        {activeTab === 'fix' && (
          <CodeBlock
            code={results.fix?.fixed_code}
            error={results.fix?.error}
            copyKey="fix"
            copiedKey={copiedKey}
            onCopy={copyToClipboard}
          />
        )}

        {/* Tab 3: Unit Tests */}
        {activeTab === 'tests' && (
          <CodeBlock
            code={results.tests?.tests}
            error={results.tests?.error}
            copyKey="tests"
            copiedKey={copiedKey}
            onCopy={copyToClipboard}
            meta={results.tests?.framework}
          />
        )}

        {/* Tab 4: Documentation */}
        {activeTab === 'docs' && (
          <CodeBlock
            code={results.docs?.documented_code}
            error={results.docs?.error}
            copyKey="docs"
            copiedKey={copiedKey}
            onCopy={copyToClipboard}
          />
        )}
      </div>
    </div>
  );
}

function CodeBlock({ code, error, copyKey, copiedKey, onCopy, meta }) {
  if (error) {
    return (
      <div className="p-3 bg-[#FEF2F2] border border-[#FECACA] rounded-[6px] text-xs text-[#DC2626]">
        <div className="font-semibold mb-0.5">Stage error:</div>
        <div>{error}</div>
      </div>
    );
  }

  return (
    <div className="relative border border-[#30363D] rounded-[6px] bg-[#0D1117] overflow-hidden">
      <div className="flex items-center justify-between px-3 py-1.5 bg-[#161B22] border-b border-[#30363D] text-[11px] font-mono text-[#8B949E]">
        <span>{meta || 'output'}</span>
        <button
          onClick={() => onCopy(code || '', copyKey)}
          disabled={!code}
          className="text-xs text-[#8B949E] hover:text-[#E6EDF3] transition-colors"
        >
          {copiedKey === copyKey ? 'Copied' : 'Copy'}
        </button>
      </div>
      <pre className="p-3.5 text-xs font-mono text-[#E6EDF3] overflow-x-auto code-scroll leading-5">
        <code>{code || '// Generating code...'}</code>
      </pre>
    </div>
  );
}
