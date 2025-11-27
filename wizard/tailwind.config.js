/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // StarMeet color palette
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
    },
  },
  plugins: [],
}
