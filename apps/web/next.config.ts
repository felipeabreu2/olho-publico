import type { NextConfig } from "next";

const config: NextConfig = {
  reactStrictMode: true,
  experimental: {
    typedRoutes: true,
  },
  images: {
    formats: ["image/avif", "image/webp"],
  },
};

export default config;
