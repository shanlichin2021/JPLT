/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Custom dark theme colors matching our CSS variables
        'primary-black': '#000000',
        'primary-grey': '#1a1a1a', 
        'secondary-grey': '#2d2d2d',
        'tertiary-grey': '#404040',
        'light-grey': '#525252',
        'border-grey': '#2d2d2d',
        'border-light': '#404040',
        
        // Text colors
        'text-primary': '#ffffff',
        'text-secondary': '#e5e5e5',
        'text-muted': '#a3a3a3',
        'text-disabled': '#737373',
        
        // Red and Indigo accent colors
        'accent-red': {
          DEFAULT: '#ef4444',
          hover: '#dc2626',
          light: '#f87171',
          dark: '#b91c1c'
        },
        'accent-indigo': {
          DEFAULT: '#6366f1',
          hover: '#4f46e5',
          light: '#818cf8',
          dark: '#3730a3'
        },
        
        // Status colors
        'success-green': '#10b981',
        'warning-orange': '#f59e0b',
        'danger-red': '#ef4444',
        'info-indigo': '#6366f1',
        
        // Surface colors
        'surface-low': '#0d0d0d',
        'surface-medium': '#1a1a1a',
        'surface-high': '#2d2d2d'
      },
      
      fontFamily: {
        'sans': ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Inter', 'system-ui', 'sans-serif']
      },
      
      borderRadius: {
        'sm': '0.375rem',
        'md': '0.5rem', 
        'lg': '0.75rem',
        'xl': '1rem'
      },
      
      boxShadow: {
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.3)',
        'md': '0 4px 6px -1px rgba(0, 0, 0, 0.4)',
        'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.5)',
        'xl': '0 20px 25px -5px rgba(0, 0, 0, 0.6)'
      },
      
      animation: {
        'slide-in': 'slideIn 0.3s ease-out',
        'fade-in': 'fadeIn 0.2s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite'
      },
      
      keyframes: {
        slideIn: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(0)' }
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        }
      }
    },
  },
  plugins: [],
}