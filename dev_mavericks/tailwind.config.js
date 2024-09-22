/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Define your custom colors here
        primary: '#006400', // Example custom color named 'primary' with hexadecimal value
        secondary: {
          light: '#ffefef', // Example custom color with light variant
          DEFAULT: '#ff5a5f', // Default (500) variant
          dark: '#e6343b', // Example custom color with dark variant
        },
    },
  },
  plugins: [],
}}