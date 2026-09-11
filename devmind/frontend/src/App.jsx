import React from 'react';
import CodeEditor from './components/CodeEditor';
import LanguageSelector from './components/LanguageSelector';
import PipelineProgress from './components/PipelineProgress';
import ResultsTabs from './components/ResultsTabs';
import PoweredByBadge from './components/PoweredByBadge';
import HowItWorks from './components/HowItWorks';
import { usePipeline } from './usePipeline';

export default function App() {
  const {
    code,
    setCode,
    language,
    setLanguage,
    isLoading,
    stageStates,
    results,
    detectedLanguage,
    errorMessage,
    runAnalysis,
  } = usePipeline();

  const handleSelectSample = (sample) => {
    setCode(sample.code);
    if (sample.language) setLanguage(sample.language);
  };

  const hasResults = Boolean(
    results.classification || results.summary || results.fix || results.tests || results.docs
  );

  return (
    <div className="min-h-screen bg-[#F9FAFB] text-[#111827] flex flex-col font-sans">
      {/* Developer Tool Header */}
      <header className="border-b border-[#E5E7EB] bg-white sticky top-0 z-30">
        <div className="max-w-[1600px] mx-auto px-4 h-13 flex items-center justify-between">
          <div className="flex items-center space-x-3 py-2.5">
            <img src="/logo.png" alt="DevMind Logo" className="h-6 w-auto object-contain" />
            <span className="font-semibold text-sm text-[#111827] tracking-tight">
              DevMind
            </span>
            <span className="text-xs text-[#6B7280]">
              Developer code diagnosis and test pipeline
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <LanguageSelector
              selectedLanguage={language}
              onSelect={setLanguage}
              disabled={isLoading}
            />
          </div>
        </div>
      </header>

      {/* Main Workspace: Dense, Two-Panel Split */}
      <main className="max-w-[1600px] w-full mx-auto p-4 flex-1 flex flex-col space-y-4">
        {/* Collapsible Explainer Section */}
        <HowItWorks />

        {/* Error Alert if any */}
        {errorMessage && (
          <div className="p-3 bg-[#FEF2F2] border border-[#FECACA] rounded-[6px] text-xs text-[#DC2626] flex items-center justify-between">
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Full-Height Two-Panel Split (Desktop) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1 items-stretch">
          {/* Left Panel: Code Input */}
          <div className="h-full flex flex-col">
            <CodeEditor
              code={code}
              onChange={setCode}
              onAnalyze={runAnalysis}
              isLoading={isLoading}
              onSelectSample={handleSelectSample}
              detectedLanguage={detectedLanguage}
            />
          </div>

          {/* Right Panel: Pipeline Progress Strip + Results */}
          <div className="h-full flex flex-col bg-white border border-[#E5E7EB] rounded-[8px] overflow-hidden">
            {/* Top Pipeline Status Strip */}
            <PipelineProgress stageStates={stageStates} />

            {/* Results Tabs Immediately Below */}
            <ResultsTabs results={results} hasResults={hasResults} />
          </div>
        </div>
      </main>

      {/* Floating Powered-By Credit Badge */}
      <PoweredByBadge />
    </div>
  );
}
