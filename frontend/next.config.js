/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable static export for desktop app bundling
  output: process.env.BUILD_MODE === 'desktop' ? 'export' : undefined,
  
  // Disable image optimization for static export
  images: {
    unoptimized: process.env.BUILD_MODE === 'desktop' ? true : false,
  },

  async rewrites() {
    // Rewrites only work in non-static mode (development)
    if (process.env.BUILD_MODE === 'desktop') return [];
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:18080/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
