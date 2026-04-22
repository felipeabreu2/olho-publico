import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: "#0a0a0a",
          subtle: "#111111",
          elevated: "#171717",
        },
        border: {
          DEFAULT: "#262626",
          subtle: "#1f1f1f",
        },
        fg: {
          DEFAULT: "#fafafa",
          muted: "#a3a3a3",
          subtle: "#737373",
        },
        accent: {
          fact: "#10b981",
          attention: "#f59e0b",
          strong: "#ef4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};

export default config;
