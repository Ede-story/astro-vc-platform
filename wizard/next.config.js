/** @type {import('next').NextConfig} */
const nextConfig = {
  // basePath: '/join', // Disabled for local dev - enable for production Nginx

  // Required for Docker deployment
  output: 'standalone',

  // Disable x-powered-by header
  poweredByHeader: false,

  // React strict mode
  reactStrictMode: true,

  // Environment variables
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://star-meet.com/star-api',
  },
}

module.exports = nextConfig
