import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    formats: ["image/avif", "image/webp"]
  },
  outputFileTracingRoot: __dirname,
  async rewrites() {
    return [
      {
        source: "/school",
        destination: "/school/index.html"
      },
      {
        source: "/uni",
        destination: "/uni/index.html"
      }
    ];
  }
};

export default nextConfig;
