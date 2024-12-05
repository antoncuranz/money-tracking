/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'standalone',
    rewrites: async () => [
        {
            source: '/api/:path*',
            destination: 'http://127.0.0.1:5000/api/:path*',
        },
    ]
}

export default nextConfig