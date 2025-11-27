/** @type {import('next').NextConfig} */
const nextConfig = {
  // Required for /join path routing via Nginx
  basePath: '/join',

  // Required for Docker deployment
  output: 'standalone',

  // Disable x-powered-by header
  poweredByHeader: false,

  // React strict mode
  reactStrictMode: true,

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://star-meet.com/api',
  },
}

module.exports = nextConfig
