/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Tema Cyberpunk
        cyber: {
          primary: '#22d3ee',
          secondary: '#0891b2',
          accent: '#67e8f9',
          dark: '#0f172a',
          darker: '#020617',
          card: '#1e293b',
          border: '#334155',
        },
        // Tema Oscuro Moderno
        dark: {
          primary: '#f8fafc',
          secondary: '#cbd5e1',
          accent: '#60a5fa',
          bg: '#0f172a',
          card: '#1e293b',
          border: '#334155',
        },
        // Tema Claro Profesional
        light: {
          primary: '#1e293b',
          secondary: '#64748b',
          accent: '#3b82f6',
          bg: '#ffffff',
          card: '#f8fafc',
          border: '#e2e8f0',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Cascadia Code', 'monospace'],
        'sans': ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.2s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s infinite',
        'pulse-once': 'pulseOnce 0.6s ease-out',
        'shimmer': 'shimmer 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-2px)' },
        },
        pulseOnce: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.02)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
      boxShadow: {
        'cyber': '0 0 20px rgba(34, 211, 238, 0.3)',
        'cyber-lg': '0 0 40px rgba(34, 211, 238, 0.2)',
      }
    },
  },
  plugins: [],
}


