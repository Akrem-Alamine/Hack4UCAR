/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        ucar: {
          blue: "#1B3A6B",
          "blue-light": "#2A5298",
          gold: "#D4A017",
          "gold-light": "#F0C040",
          bg: "#F5F7FA",
          sidebar: "#0F2347",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
