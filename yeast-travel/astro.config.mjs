import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: process.env.SITE_URL || "https://yeast-travel.lilac9406.chatgpt.site",
  output: "static",
  integrations: [sitemap()],
  vite: {
    build: {
      cssMinify: true,
    },
  },
});
