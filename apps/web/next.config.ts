import type { NextConfig } from "next";
import path from "node:path";

const config: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  // Em monorepo pnpm, standalone precisa rastrear deps a partir da raiz do
  // repositório, não só do apps/web — caso contrário falta @olho/db, etc.
  outputFileTracingRoot: path.join(import.meta.dirname, "../../"),
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default config;
