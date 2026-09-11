import { useState, useCallback } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function usePipeline() {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [activeStage, setActiveStage] = useState(null);
  const [stageStates, setStageStates] = useState({});
  const [results, setResults] = useState({});
  const [errorMessage, setErrorMessage] = useState(null);

  const resetPipeline = useCallback(() => {
    setStageStates({});
    setResults({});
    setActiveStage(null);
    setErrorMessage(null);
  }, []);

  const runAnalysis = useCallback(async () => {
    if (!code.trim() || isLoading) return;

    setIsLoading(true);
    resetPipeline();

    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code, language }),
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}: ${await response.text()}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop() || '';

        for (const rawEvent of events) {
          if (!rawEvent.trim()) continue;
          const lines = rawEvent.split('\n');
          let eventType = '';
          let dataStr = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) eventType = line.replace('event: ', '').trim();
            if (line.startsWith('data: ')) dataStr = line.replace('data: ', '').trim();
          }

          if (!eventType || !dataStr) continue;

          try {
            const data = JSON.parse(dataStr);
            if (eventType === 'stage_update') {
              setActiveStage(data.stage);
              setStageStates((prev) => ({
                ...prev,
                [data.stage]: { status: data.status, label: data.label },
              }));
            } else if (eventType === 'stage_complete') {
              setStageStates((prev) => ({
                ...prev,
                [data.stage]: { status: data.result?.skipped ? 'skipped' : 'complete' },
              }));
              if (data.stage === 1) setResults((r) => ({ ...r, classification: data.result }));
              if (data.stage === 2) setResults((r) => ({ ...r, summary: data.result }));
              if (data.stage === 3) setResults((r) => ({ ...r, fix: data.result }));
              if (data.stage === 4) setResults((r) => ({ ...r, tests: data.result }));
              if (data.stage === 5) setResults((r) => ({ ...r, docs: data.result }));
            } else if (eventType === 'done') {
              if (data.full_result) setResults(data.full_result);
              setActiveStage(null);
            }
          } catch (parseErr) {
            console.warn('Failed to parse SSE payload:', parseErr, dataStr);
          }
        }
      }
    } catch (err) {
      console.error('Pipeline error:', err);
      setErrorMessage(err.message || 'Pipeline analysis failed. Ensure the backend is running.');
    } finally {
      setIsLoading(false);
      setActiveStage(null);
    }
  }, [code, language, isLoading, resetPipeline]);

  return {
    code,
    setCode,
    language,
    setLanguage,
    isLoading,
    activeStage,
    stageStates,
    results,
    detectedLanguage: results.classification?.language || null,
    errorMessage,
    runAnalysis,
    resetPipeline,
  };
}
