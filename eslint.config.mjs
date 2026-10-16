import nextCoreWebVitals from "eslint-config-next/core-web-vitals";
import nextTypescript from "eslint-config-next/typescript";

/**
 * Next 16 ile birlikte gelen duz (flat) yapilandirma.
 * FlatCompat kullanilmaz - eslint 9.39 ile dongusel yapilandirma hatasi veriyor.
 */
const eslintConfig = [
  { ignores: [".next/**", "node_modules/**", "drizzle/**", "public/**", "deploy/**", "storage/**", "next-env.d.ts"] },
  ...nextCoreWebVitals,
  ...nextTypescript,
  {
    rules: {
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "@next/next/no-img-element": "off",
    },
  },
];

export default eslintConfig;
