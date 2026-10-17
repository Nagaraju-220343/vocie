import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  allowedDevOrigins: [
    "*.ngrok-free.dev",
    "*.ngrok-free.app",
    "*.ngrok.io",
    "directly-blasphemy-doormat.ngrok-free.dev",
  ],
  async rewrites() {
    const backendUrl = process.env.BACKEND_INTERNAL_URL || process.env.NEXT_PUBLIC_SOCKET_URL || "https://restaurant-voice-backend-adq1.onrender.com";
    return [
      {
        source: "/api/calls/:path*",
        destination: `${backendUrl}/api/calls/:path*`,
      },
      {
        source: "/api/orders/:path*",
        destination: `${backendUrl}/api/orders/:path*`,
      },
      {
        source: "/api/customers/:path*",
        destination: `${backendUrl}/api/customers/:path*`,
      },
      {
        source: "/api/faqs/:path*",
        destination: `${backendUrl}/api/faqs/:path*`,
      },
      {
        source: "/api/feedback/:path*",
        destination: `${backendUrl}/api/feedback/:path*`,
      },
      {
        source: "/api/voice/:path*",
        destination: `${backendUrl}/api/voice/:path*`,
      },
      {
        source: "/api/webhooks/:path*",
        destination: `${backendUrl}/api/webhooks/:path*`,
      },
      {
        source: "/api/health",
        destination: `${backendUrl}/api/health`,
      },
      {
        source: "/socket.io/:path*",
        destination: `${backendUrl}/socket.io/:path*`,
      },
    ];
  },
};

export default nextConfig;
