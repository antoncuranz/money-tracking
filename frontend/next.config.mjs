/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export', // Outputs a Single-Page Application (SPA).
    distDir: './build', // Changes the build output directory to `./dist`.
    rewrites: async () => [
        {
            source: '/api/:path*',
            destination: 'http://127.0.0.1:5000/api/:path*',
        },
    ]
}

export default nextConfig