/** @type {import('next').NextConfig} */
const BACKEND = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig = {
  // Emit a self-contained .next/standalone build (minimal server.js, no full
  // node_modules) so the production Docker image stays small. See ui/Dockerfile.
  output: "standalone",
  typedRoutes: true,
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${BACKEND}/api/:path*` },
    ];
  },
};

export default nextConfig;
