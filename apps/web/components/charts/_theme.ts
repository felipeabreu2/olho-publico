/**
 * Tema unificado para todos os gráficos recharts.
 * Mantém consistência visual com o design system do projeto.
 */
export const chartTheme = {
  colors: {
    primary: "#fafafa",
    grid: "#262626",
    axis: "#737373",
    tooltipBg: "#171717",
    tooltipBorder: "#262626",
    accent: {
      fact: "#10b981",
      attention: "#f59e0b",
      strong: "#ef4444",
    },
    palette: [
      "#10b981", // verde
      "#06b6d4", // ciano
      "#a855f7", // roxo
      "#f59e0b", // âmbar
      "#ef4444", // vermelho
      "#ec4899", // rosa
      "#84cc16", // lime
      "#3b82f6", // azul
    ],
  },
  font: {
    family: "var(--font-inter), Inter, system-ui, sans-serif",
    mono: "var(--font-mono), 'JetBrains Mono', monospace",
    sizeAxis: 11,
    sizeLabel: 12,
  },
} as const;
