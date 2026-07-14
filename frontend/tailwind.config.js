export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"]
      },
      colors: {
        ink: "#e6edf7",
        cloud: "#050b16",
        steel: "#9ba8bd",
        mint: "#2dd4bf",
        amber: "#fbbf24"
      }
    }
  },
  plugins: []
};
