import type { Interest, PaidOffer, PracticalGuide } from "./types";

export const interestLabels: Record<Interest, string> = {
  "first-time": "First time",
  food: "Food",
  "local-life": "Local life",
  "art-craft": "Art & craft",
};

export const practicalGuides: PracticalGuide[] = [
  {
    slug: "payments-in-china",
    title: "Paying in China without panic",
    dek: "A calm setup checklist for cards, mobile wallets and the moments when cash still helps.",
    updated: "2026-07-19",
    sections: [
      { heading: "Before you fly", body: "Install the international version of Alipay or WeChat, complete identity checks, and add more than one bank card. Do this before arrival so you are not troubleshooting on the pavement.", tips: ["Tell your bank you are travelling", "Keep a physical card and a small cash backup", "Never share one-time verification codes"] },
      { heading: "At the counter", body: "Small shops commonly ask you to scan their QR code; larger merchants can usually scan yours. Check the amount before confirming and keep the payment result on screen until the seller sees it." },
      { heading: "When it fails", body: "Try the second wallet or card, ask whether a physical card is accepted, or use cash. A failed payment is inconvenient, not a travel emergency." },
    ],
  },
  {
    slug: "maps-in-china",
    title: "Maps that work in China",
    dek: "How to use bilingual names, Chinese addresses and Amap links without depending on live location.",
    updated: "2026-07-19",
    sections: [
      { heading: "Use the Chinese address", body: "English place names can be inconsistent. Every Yeast stop includes the Chinese name and address so you can paste the exact destination into Amap or show it to a driver." },
      { heading: "Treat routes as a sequence", body: "Our day plans are pre-arranged in a practical order. Even when a map does not load, the time line, transport note and copyable address remain available." },
      { heading: "Do not rely on GPS alone", body: "Large complexes may have several entrances. Match the Chinese name, nearby landmark and arrival note before walking the final block." },
    ],
  },
  {
    slug: "china-trains",
    title: "China trains, step by step",
    dek: "The simple version: book with your passport name, arrive early and follow the train number.",
    updated: "2026-07-19",
    sections: [
      { heading: "Booking", body: "Use the official Railway 12306 service or a reputable OTA. Enter your name exactly as shown in your passport and recheck the station: many cities have several." },
      { heading: "At the station", body: "Bring the same physical passport used for booking. Arrive 45–60 minutes early for security and wayfinding, especially at a station you have not used before." },
      { heading: "Boarding", body: "Follow the train number rather than the English destination alone. Your screen announces the gate and the platform markings show where each carriage stops." },
    ],
  },
  {
    slug: "bookings-and-tickets",
    title: "Bookings, tickets and closed Mondays",
    dek: "A lightweight routine for museums, timed entries and attraction closures.",
    updated: "2026-07-19",
    sections: [
      { heading: "Check again 48 hours before", body: "Reservation systems and opening rules change. Follow the official venue account or site, use your passport details, and screenshot the confirmation." },
      { heading: "Build around the fragile stop", body: "If one museum needs a timed entry, anchor the day around it. Flexible streets, parks and food stops can move; the reservation usually cannot." },
      { heading: "Use the backup", body: "Every Yeast route names a rain or closure alternative. Switching is part of the plan, not a failed trip." },
    ],
  },
];

export const paidOffers: PaidOffer[] = [
  {
    slug: "shanghai-side-quest",
    name: "Shanghai Side Quest",
    city: "shanghai",
    status: "COMING_SOON",
    partner: "Yeast Travel",
    fulfiller: "Yeast Travel",
    qualification: "Field verification in progress",
    language: "English",
    price: "Not on sale",
    duration: "2–3 hours",
    cancellation: "No booking is currently accepted.",
    disclosure: "A Yeast Travel original. This preview is not a purchasable tour.",
  },
];
