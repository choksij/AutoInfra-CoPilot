/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{ts,tsx,js,jsx}",
    "./components/**/*.{ts,tsx,js,jsx}",
    "./lib/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        // tokens used in globals.css
        background: "var(--bg)",
        foreground: "var(--fg)",
        panel: "var(--panel)",
        muted: "var(--muted)",
        critical: "#ef4444",
        high: "#f59e0b",
        medium: "#3b82f6",
        low: "#10b981",
      },
      boxShadow: {
        // 👇 this makes `shadow-soft` valid
        soft: "0 10px 30px -12px rgba(0, 0, 0, 0.25)",
      },
      borderRadius: {
        "2xl": "1rem",
      },
    },
  },
  plugins: [],
};
