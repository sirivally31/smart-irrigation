import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        farm: {
          dark: "#133E32",
          primary: "#1B4D3E",
          emerald: "#2D7A4D",
          leaf: "#4E9F3D",
          light: "#E8F5E9",
          cream: "#FBFBF7",
          sand: "#F5F7F2",
          soil: "#854D0E",
          amber: "#D97706",
          water: "#0284C7",
          dry: "#DC2626",
          optimal: "#16A34A"
        }
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "Noto Sans Devanagari", "Noto Sans Kannada", "sans-serif"]
      }
    },
  },
  plugins: [],
};
export default config;
