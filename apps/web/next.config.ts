import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default config;
