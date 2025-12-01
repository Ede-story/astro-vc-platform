/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // StarMeet Brand Colors
        brand: {
          green: '#6B9B37',
          'green-hover': '#5a8a2d',
          graphite: '#2f3538',
          'graphite-hover': '#3d4448',
        },
        // Legacy palette
        starmeet: {
          dark: '#0a0a1a',
          darker: '#050510',
          purple: '#6b21a8',
          'purple-light': '#9333ea',
          blue: '#1e3a8a',
          'blue-light': '#3b82f6',
          gold: '#f59e0b',
        }
      },
      fontFamily: {
        sans: ['var(--font-montserrat)', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
