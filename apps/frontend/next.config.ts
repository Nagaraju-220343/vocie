import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    return [
      {
        source: "/api/calls/:path*",
        destination: "http://localhost:8000/api/calls/:path*",
      },
      {
        source: "/api/orders/:path*",
        destination: "http://localhost:8000/api/orders/:path*",
      },
      {
        source: "/api/customers/:path*",
        destination: "http://localhost:8000/api/customers/:path*",
      },
      {
        source: "/api/faqs/:path*",
        destination: "http://localhost:8000/api/faqs/:path*",
      },
      {
        source: "/api/feedback/:path*",
        destination: "http://localhost:8000/api/feedback/:path*",
      },
      {
        source: "/api/voice/:path*",
        destination: "http://localhost:8000/api/voice/:path*",
      },
      {
        source: "/api/webhooks/:path*",
        destination: "http://localhost:8000/api/webhooks/:path*",
      },
      {
        source: "/api/health",
        destination: "http://localhost:8000/api/health",
      },
      {
        source: "/socket.io/:path*",
        destination: "http://localhost:8000/socket.io/:path*",
      },
    ];
  },
};

export default nextConfig;
