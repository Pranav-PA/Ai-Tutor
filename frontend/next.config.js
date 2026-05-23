/** @type {import('next').NextConfig} */
const isDesktop = process.env.BUILD_MODE === 'desktop';

const nextConfig = {
  // Use standalone output for desktop (not static export) to support dynamic routes
  output: isDesktop ? 'standalone' : undefined,
  
  // Disable image optimization for desktop builds
  images: {
    unoptimized: isDesktop,
  },

  // Rewrites only apply in development (not in standalone/desktop mode)
  ...(isDesktop ? {} : {
    async rewrites() {
      return [
        {
          source: '/api/:path*',
          destination: 'http://localhost:18080/api/:path*',
        },
      ];
    },
  }),
};

module.exports = nextConfig;
