import { z } from "zod";

const status = z.enum(["DRAFT", "RESEARCHED", "ROUTE_CHECKED", "PUBLISHED", "PAUSED"]);
const interest = z.enum(["first-time", "food", "local-life", "art-craft"]);
const citySlug = z.enum(["shanghai", "hangzhou", "suzhou", "jingdezhen"]);
const requiredText = z.string().trim().min(1);

const stopSchema = z.object({
  id: requiredText, name: requiredText, nameZh: requiredText,
  address: requiredText, addressZh: requiredText,
  coordinates: z.tuple([z.number(), z.number()]).optional(),
  duration: requiredText, cost: requiredText, arrival: requiredText,
  note: requiredText, opening: requiredText, booking: requiredText,
  fallback: requiredText, amapUrl: z.url(), sourceUrl: z.url(),
  sourceLabel: requiredText, lastChecked: z.iso.date(),
});

const routeSchema = z.object({
  slug: requiredText, city: citySlug, day: z.union([z.literal(1), z.literal(2), z.literal(3)]),
  name: requiredText, shortName: requiredText, summary: requiredText,
  duration: requiredText, pace: z.enum(["easy", "balanced", "full"]),
  interests: z.array(interest).min(1), accent: z.enum(["coral", "violet", "lime", "sky"]),
  status, verification: z.enum(["DESK_CHECKED_BETA", "FIELD_CHECKED"]),
  lastChecked: z.iso.date(), rainyDay: requiredText, closureBackup: requiredText,
  mapUrl: z.url(), stops: z.array(stopSchema).min(3),
});

const citySchema = z.object({
  slug: citySlug, name: requiredText, nameZh: requiredText, region: requiredText,
  idealDays: requiredText, character: requiredText, intro: requiredText,
  arrival: requiredText, season: requiredText,
  accent: z.enum(["coral", "violet", "lime", "sky"]), status,
});

export function validateCatalog(cities: unknown[], routes: unknown[]) {
  const parsedCities = z.array(citySchema).length(4).parse(cities);
  const parsedRoutes = z.array(routeSchema).length(12).parse(routes);
  const routeSlugs = new Set(parsedRoutes.map((route) => route.slug));
  if (routeSlugs.size !== parsedRoutes.length) throw new Error("Route slugs must be unique.");
  const allStops = parsedRoutes.flatMap((route) => route.stops);
  if (allStops.length < 36) throw new Error("The launch catalog requires at least 36 route stops.");
  const stopIds = new Set(allStops.map((stop) => stop.id));
  if (stopIds.size !== allStops.length) throw new Error("Stop ids must be unique.");
  for (const city of parsedCities) {
    const days = parsedRoutes.filter((route) => route.city === city.slug).map((route) => route.day).sort();
    if (days.join(",") !== "1,2,3") throw new Error(`${city.slug} must have exactly Day 1, Day 2 and Day 3 modules.`);
  }
}
