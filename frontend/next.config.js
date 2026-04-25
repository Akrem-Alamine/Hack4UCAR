/** @type {import('next').NextConfig} */
const isStaticExport = process.env.NEXT_STATIC_EXPORT === "true";

const nextConfig = {
  // Static export only for GitHub Pages CI — Docker/local runs as a proper server
  ...(isStaticExport ? { output: "export" } : {}),
  trailingSlash: true,
  images: { unoptimized: true },
  basePath: isStaticExport ? (process.env.NEXT_PUBLIC_BASE_PATH || "") : "",
};

module.exports = nextConfig;
