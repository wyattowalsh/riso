/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Manrope"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['"Fraunces"', 'ui-serif', 'Georgia', 'serif'],
      },
      colors: {
        riso: {
          // Original scale
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0078BF',  // Updated to federal blue
          600: '#005A8F',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
          // Riso Ink colors
          'federal-blue': '#0078BF',
          'bright-red': '#FF665E',
          'sunflower': '#FFE800',
          'green': '#00A95C',
          'orange': '#FF6C2F',
          'fluorescent-pink': '#FF48B0',
          'teal': '#00838A',
          'grape': '#765BA7',
          // Extended inks
          'cornflower': '#62A8E5',
          'sea-blue': '#0074A2',
          'mint': '#82D8D5',
          'hunter-green': '#407060',
          'apricot': '#F6A04D',
          'gold': '#BB8B41',
          'burgundy': '#914E72',
          // Paper textures
          'cream': '#F5F1EA',
          'paper-white': '#FFFEF9',
          'kraft': '#E8DFD0',
          'newsprint': '#F0EDE5',
          // Dark mode
          'ink-black': '#0F172A',
          'charcoal': '#1E293B',
          'graphite': '#334155',
          'slate': '#475569',
        },
      },
    },
  },
  plugins: [],
}
