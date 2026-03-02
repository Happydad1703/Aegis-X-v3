import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        cic: {
          bg: "#0f1419",
          card: "#161b22",
          border: "#30363d",
          muted: "#8b949e",
          accent: "#58a6ff",
          danger: "#f85149",
          success: "#3fb950",
          warn: "#d29922",
        },
      },
    },
  },
  plugins: [],
};
export default config;
