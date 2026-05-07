/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["Work Sans", "sans-serif"],
      },
      colors: {
        // §12 Tier colors
        "tier-s":         "#22C55E",
        "tier-a":         "#60A5FA",
        "tier-b":         "#F59E0B",
        "tier-c":         "#EF4444",
        "tier-impaired":  "#7C3AED",
        "tier-debtfree":  "#60A5FA",
        "tier-unknown":   "#475569",
        // 6-stat axis colors
        "stat-profit":    "#3B82F6",
        "stat-growth":    "#10B981",
        "stat-stability": "#F59E0B",
        "stat-efficiency":"#8B5CF6",
        "stat-valuation": "#EC4899",
        "stat-cash":      "#06B6D4",
      },
    },
  },
  plugins: [],
};
