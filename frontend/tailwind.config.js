export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ["Space Grotesk", "sans-serif"],
        body: ["Manrope", "sans-serif"]
      },
      colors: {
        ink: "#0f172a",
        cloud: "#f8fafc",
        steel: "#334155",
        mint: "#0ea5a4",
        amber: "#f59e0b"
      }
    }
  },
  plugins: []
};
