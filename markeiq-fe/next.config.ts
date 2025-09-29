import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    // Temporarily allow images from any host.
    // WARNING: This is not recommended for production due to security implications.
    // In a production environment, you should list specific allowed hostnames
    // or use more restrictive patterns.
    remotePatterns: [
      {
        hostname: '**', // Matches any hostname
        pathname: '**', // Matches any path
      },
    ],
  },
};

export default nextConfig;
