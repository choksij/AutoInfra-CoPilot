/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        ink: {
          900: "#0B1020",
          800: "#151B2B",
          700: "#1E2435"
        }
      },
      boxShadow: {
        soft: "0 6px 24px rgba(0,0,0,0.08)"
      },
      borderRadius: {
        xl2: "1rem"
      }
    }
  },
  plugins: []
};
