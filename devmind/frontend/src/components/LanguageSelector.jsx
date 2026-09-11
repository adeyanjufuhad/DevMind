import React from 'react';

const SUPPORTED_LANGUAGES = [
  { value: "", label: "Auto-detect language" },
  { value: "python", label: "Python" },
  { value: "javascript", label: "JavaScript" },
  { value: "typescript", label: "TypeScript" },
  { value: "go", label: "Go" },
  { value: "rust", label: "Rust" },
  { value: "java", label: "Java" },
  { value: "cpp", label: "C++" },
  { value: "csharp", label: "C#" },
  { value: "ruby", label: "Ruby" },
  { value: "php", label: "PHP" },
];

export default function LanguageSelector({ selectedLanguage, onSelect, disabled }) {
  return (
    <div className="flex items-center space-x-2">
      <label htmlFor="language-select" className="text-xs text-[#6B7280] font-medium">
        Language
      </label>
      <select
        id="language-select"
        value={selectedLanguage || ""}
        onChange={(e) => onSelect(e.target.value || null)}
        disabled={disabled}
        className="bg-white text-[#111827] text-xs font-medium rounded-[6px] px-2.5 py-1.5 border border-[#E5E7EB] hover:border-[#D1D5DB] focus:outline-none focus:border-[#2563EB] transition-colors cursor-pointer disabled:opacity-50"
      >
        {SUPPORTED_LANGUAGES.map((lang) => (
          <option key={lang.value} value={lang.value}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}
