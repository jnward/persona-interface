import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable static HTML export so the app can be served without a Node runtime.
  output: 'export',
};

export default nextConfig;
