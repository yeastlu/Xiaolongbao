export const citySlugs = ["shanghai", "hangzhou", "suzhou", "jingdezhen"] as const;
export const interests = ["first-time", "food", "local-life", "art-craft"] as const;

export type CitySlug = (typeof citySlugs)[number];
export type Interest = (typeof interests)[number];
export type PublishStatus = "DRAFT" | "RESEARCHED" | "ROUTE_CHECKED" | "PUBLISHED" | "PAUSED";

export interface Stop {
  id: string;
  name: string;
  nameZh: string;
  address: string;
  addressZh: string;
  coordinates?: [number, number];
  duration: string;
  cost: string;
  arrival: string;
  note: string;
  opening: string;
  booking: string;
  fallback: string;
  amapUrl: string;
  sourceUrl: string;
  sourceLabel: string;
  lastChecked: string;
}

export interface RouteModule {
  slug: string;
  city: CitySlug;
  day: 1 | 2 | 3;
  name: string;
  shortName: string;
  summary: string;
  duration: string;
  pace: "easy" | "balanced" | "full";
  interests: Interest[];
  accent: "coral" | "violet" | "lime" | "sky";
  status: PublishStatus;
  verification: "DESK_CHECKED_BETA" | "FIELD_CHECKED";
  lastChecked: string;
  rainyDay: string;
  closureBackup: string;
  mapUrl: string;
  stops: Stop[];
}

export interface City {
  slug: CitySlug;
  name: string;
  nameZh: string;
  region: string;
  idealDays: string;
  character: string;
  intro: string;
  arrival: string;
  season: string;
  accent: "coral" | "violet" | "lime" | "sky";
  status: PublishStatus;
}

export interface PracticalGuide {
  slug: string;
  title: string;
  dek: string;
  updated: string;
  sections: Array<{ heading: string; body: string; tips?: string[] }>;
}

export interface PaidOffer {
  slug: string;
  name: string;
  city: CitySlug;
  status: PublishStatus | "COMING_SOON";
  partner: string;
  fulfiller: string;
  qualification: string;
  language: string;
  price: string;
  duration: string;
  cancellation: string;
  disclosure: string;
  url?: string;
}
