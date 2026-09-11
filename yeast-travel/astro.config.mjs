import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: process.env.SITE_URL || "https://yeast-travel.netlify.app",
  output: "static",
  integrations: [sitemap()],
  vite: {
    build: {
      cssMinify: true,
    },
  },
});
