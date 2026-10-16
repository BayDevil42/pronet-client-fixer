import type { NextConfig } from "next";

/**
 * Güvenlik başlıkları. CSP, reklam (AdSense/GAM), analytics (GA4/GTM) ve
 * gömülü video (YouTube/Vimeo) için gerekli kaynaklara izin verir.
 */
const CSP = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://pagead2.googlesyndication.com https://securepubads.g.doubleclick.net https://www.googletagmanager.com https://www.google-analytics.com",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob: https:",
  "font-src 'self' data:",
  "connect-src 'self' https://www.google-analytics.com https://api.coingecko.com https://www.tcmb.gov.tr",
  "frame-src 'self' https://www.youtube.com https://www.youtube-nocookie.com https://player.vimeo.com https://googleads.g.doubleclick.net https://tpc.googlesyndication.com",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'self'",
  "upgrade-insecure-requests",
].join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: CSP },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "SAMEORIGIN" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=(), interest-cohort=()" },
  { key: "X-DNS-Prefetch-Control", value: "on" },
  {
    key: "Strict-Transport-Security",
    value: "max-age=63072000; includeSubDomains; preload",
  },
];

const nextConfig: NextConfig = {
  // cPanel/Passenger deploy'u için tek klasörlük çıktı.
  output: "standalone",
  reactStrictMode: true,
  poweredByHeader: false,
  compress: true,
  productionBrowserSourceMaps: false,

  // Görsel varyantları upload anında sharp ile üretiliyor; runtime optimizer
  // paylaşımlı hosting CPU/RAM'ini tüketmesin diye kapalı.
  images: {
    unoptimized: true,
    formats: ["image/avif", "image/webp"],
  },

  // Native modüller bundle edilmemeli.
  serverExternalPackages: ["better-sqlite3", "sharp"],

  typescript: { ignoreBuildErrors: false },

  async headers() {
    return [
      { source: "/:path*", headers: securityHeaders },
      {
        source: "/uploads/:path*",
        headers: [
          { key: "Cache-Control", value: "public, max-age=31536000, immutable" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Content-Disposition", value: "inline" },
        ],
      },
    ];
  },
};

export default nextConfig;
