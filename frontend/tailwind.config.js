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
        primary: {
          DEFAULT: '#050505', // Deep Black
          light: '#1A1A1A',
          dark: '#000000',
        },
        piggy: {
          DEFAULT: '#FF99AA', // Piggy Bank Pink
          light: '#FFB3C1',
          dark: '#E07A8A',
        },
        metal: {
          gold: '#D4AF37',
          silver: '#C0C0C0',
          copper: '#B87333',
        },
        accent: {
          DEFAULT: '#FF99AA', // Defaults to Piggy Pink
          foreground: '#050505',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'premium': '0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 10px -2px rgba(0, 0, 0, 0.04)',
        'premium-hover': '0 10px 30px -5px rgba(0, 0, 0, 0.08), 0 4px 15px -5px rgba(0, 0, 0, 0.06)',
      }
    },
  },
  plugins: [],
}
