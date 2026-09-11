/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        base: '#F9FAFB',
        surface: {
          DEFAULT: '#FFFFFF',
          secondary: '#F3F4F6',
        },
        border: {
          DEFAULT: '#E5E7EB',
          dark: '#30363D',
        },
        accent: {
          DEFAULT: '#2563EB',
          hover: '#1D4ED8',
          subtle: '#EFF6FF',
        },
        success: {
          DEFAULT: '#16A34A',
          subtle: '#F0FDF4',
        },
        error: {
          DEFAULT: '#DC2626',
          subtle: '#FEF2F2',
        },
        text: {
          primary: '#111827',
          secondary: '#6B7280',
        },
        code: {
          bg: '#0D1117',
          panel: '#161B22',
          border: '#30363D',
          gutter: '#8B949E',
          cursor: '#58A6FF',
          fg: '#E6EDF3',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      boxShadow: {
        badge: '0 1px 3px rgba(0,0,0,0.08)',
        none: 'none',
      },
      borderRadius: {
        DEFAULT: '6px',
        md: '6px',
        lg: '8px',
      }
    },
  },
  plugins: [],
}
