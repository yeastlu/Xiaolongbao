import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: process.env.SITE_URL || "https://effervescent-squirrel-8e44a1.netlify.app",
  output: "static",
  integrations: [sitemap()],
  vite: {
    build: {
      cssMinify: true,
    },
  },
});
