import type { Category, Customer, Merchant, Trigger } from "@/lib/types";

export const CATEGORIES: Record<string, Category> = {
  dentists: {
    slug: "dentists",
    display_name: "Dentists",
    voice: { tone: "peer_clinical" },
    peer_stats: { avg_ctr: 0.03, avg_rating: 4.4, avg_calls_30d: 12 },
    digest: [
      {
        id: "d_2026W17_jida_fluoride",
        kind: "research",
        title: "3-month fluoride recall cuts caries 38% better than 6-month",
        source: "JIDA Oct 2026, p.14",
        trial_n: 2100,
        patient_segment: "high_risk_adults",
      },
      {
        id: "d_2026W17_dci_radiograph",
        kind: "compliance",
        title: "DCI revised radiograph dose limits effective 2026-12-15",
        source: "DCI circular 2026-11-04",
      },
    ],
  },
  salons: {
    slug: "salons",
    display_name: "Salons",
    voice: { tone: "warm_beauty" },
    peer_stats: { avg_ctr: 0.042, avg_rating: 4.5 },
    digest: [],
  },
  restaurants: {
    slug: "restaurants",
    display_name: "Restaurants",
    voice: { tone: "operator_food" },
    peer_stats: { avg_ctr: 0.038, avg_rating: 4.3 },
    digest: [],
  },
};

export const MERCHANTS: Merchant[] = [
  {
    merchant_id: "m_001_drmeera_dentist_delhi",
    category_slug: "dentists",
    identity: {
      name: "Dr. Meera's Dental Clinic",
      city: "Delhi",
      locality: "Lajpat Nagar",
      owner_first_name: "Meera",
      verified: true,
      languages: ["en", "hi"],
    },
    subscription: { status: "active", plan: "Pro", days_remaining: 82 },
    performance: {
      views: 2410,
      calls: 18,
      ctr: 0.021,
      directions: 45,
      delta_7d: { views_pct: 0.18, calls_pct: -0.05 },
    },
    offers: [
      { id: "o1", title: "Dental Cleaning @ ₹299", status: "active" },
      { id: "o2", title: "Deep Cleaning @ ₹499", status: "expired" },
    ],
    signals: ["stale_posts:22d", "ctr_below_peer_median", "high_risk_adult_cohort"],
    customer_aggregate: { total_unique_ytd: 540, retention_6mo_pct: 0.38 },
    conversation_history: [
      {
        ts: "2026-04-24T10:12:00Z",
        from: "vera",
        body: "Google posts are stale (last post 22 days ago). Want me to draft 3 posts?",
      },
    ],
  },
  {
    merchant_id: "m_002_bharat_dentist_mumbai",
    category_slug: "dentists",
    identity: {
      name: "Bharat Dental Care",
      city: "Mumbai",
      locality: "Andheri West",
      owner_first_name: "Bharat",
      verified: false,
      languages: ["en", "hi", "mr"],
    },
    subscription: { status: "active", plan: "Pro", days_remaining: 12 },
    performance: {
      views: 980,
      calls: 4,
      ctr: 0.018,
      delta_7d: { calls_pct: -0.5 },
    },
    offers: [],
    signals: ["renewal_due_soon:12d", "perf_dip_severe", "no_active_offers"],
    customer_aggregate: { total_unique_ytd: 220 },
  },
  {
    merchant_id: "m_003_studio11_salon_hyderabad",
    category_slug: "salons",
    identity: {
      name: "Studio11 Family Salon",
      city: "Hyderabad",
      locality: "Kapra",
      owner_first_name: "Lakshmi",
      verified: true,
    },
    subscription: { status: "active", plan: "Pro", days_remaining: 145 },
    performance: { views: 4980, calls: 62, ctr: 0.048 },
    offers: [
      { id: "o1", title: "Haircut @ ₹99", status: "active" },
      { id: "o2", title: "Hair Spa @ ₹499", status: "active" },
    ],
    signals: ["high_engagement", "above_peer_median_calls"],
  },
  {
    merchant_id: "m_005_pizzajunction_restaurant_delhi",
    category_slug: "restaurants",
    identity: {
      name: "Pizza Junction",
      city: "Delhi",
      locality: "Sector 14",
      owner_first_name: "Raj",
      verified: true,
    },
    subscription: { status: "active", plan: "Pro", days_remaining: 60 },
    performance: { views: 3200, calls: 45, ctr: 0.035 },
    offers: [{ id: "o1", title: "Large Pizza @ ₹299", status: "active" }],
    signals: ["delivery_reviews_rising"],
  },
];

export const CUSTOMERS: Customer[] = [
  {
    customer_id: "c_001_priya_for_m001",
    merchant_id: "m_001_drmeera_dentist_delhi",
    identity: { name: "Priya", language_pref: "hi-en mix" },
    relationship: { last_visit: "2026-05-12", visits_total: 4 },
    state: "lapsed_soft",
    consent: { scope: ["recall_reminders", "appointment_reminders"] },
  },
];

export const TRIGGERS: Trigger[] = [
  {
    id: "trg_001_research_digest_dentists",
    scope: "merchant",
    kind: "research_digest",
    source: "external",
    merchant_id: "m_001_drmeera_dentist_delhi",
    customer_id: null,
    payload: { category: "dentists", top_item_id: "d_2026W17_jida_fluoride" },
    urgency: 2,
    suppression_key: "research:dentists:2026-W17",
    expires_at: "2026-05-03T00:00:00Z",
  },
  {
    id: "trg_002_compliance_dci_radiograph",
    scope: "merchant",
    kind: "regulation_change",
    merchant_id: "m_001_drmeera_dentist_delhi",
    customer_id: null,
    payload: { category: "dentists", top_item_id: "d_2026W17_dci_radiograph", deadline_iso: "2026-12-15" },
    urgency: 4,
    suppression_key: "compliance:dci_radiograph:2026",
  },
  {
    id: "trg_003_recall_due_priya",
    scope: "customer",
    kind: "recall_due",
    merchant_id: "m_001_drmeera_dentist_delhi",
    customer_id: "c_001_priya_for_m001",
    payload: {
      service_due: "6_month_cleaning",
      available_slots: [
        { label: "Wed 5 Nov, 6pm" },
        { label: "Thu 6 Nov, 5pm" },
      ],
    },
    urgency: 3,
    suppression_key: "recall:c_001_priya_for_m001:6mo",
  },
  {
    id: "trg_004_perf_dip_bharat",
    scope: "merchant",
    kind: "perf_dip",
    merchant_id: "m_002_bharat_dentist_mumbai",
    customer_id: null,
    payload: { metric: "calls", delta_pct: -0.5 },
    urgency: 4,
    suppression_key: "perf_dip:m_002:calls",
  },
  {
    id: "trg_005_renewal_due_bharat",
    scope: "merchant",
    kind: "renewal_due",
    merchant_id: "m_002_bharat_dentist_mumbai",
    customer_id: null,
    payload: { days_remaining: 12, plan: "Pro", renewal_amount: 4999 },
    urgency: 4,
    suppression_key: "renewal:m_002:2026-Q2",
  },
  {
    id: "trg_006_festival_diwali",
    scope: "merchant",
    kind: "festival_upcoming",
    merchant_id: "m_003_studio11_salon_hyderabad",
    customer_id: null,
    payload: { festival: "Diwali", days_until: 30 },
    urgency: 2,
    suppression_key: "festival:diwali:2026",
  },
  {
    id: "trg_011_review_theme_late_delivery",
    scope: "merchant",
    kind: "review_theme_emerged",
    merchant_id: "m_005_pizzajunction_restaurant_delhi",
    customer_id: null,
    payload: { theme: "delivery_late", occurrences_30d: 4 },
    urgency: 3,
    suppression_key: "review_theme:m_005:delivery",
  },
];

export const TRIGGER_KINDS = [
  "research_digest",
  "renewal_due",
  "recall_due",
  "festival",
  "review_request",
  "regulation_change",
  "performance_drop",
  "customer_followup",
  "subscription_expiry",
  "active_offer",
] as const;

export function getMerchant(id: string): Merchant | undefined {
  return MERCHANTS.find((m) => m.merchant_id === id);
}

export function getTriggersForMerchant(merchantId: string): Trigger[] {
  return TRIGGERS.filter((t) => t.merchant_id === merchantId);
}

export function getCategory(slug: string): Category | undefined {
  return CATEGORIES[slug];
}

export function getCustomer(id: string): Customer | undefined {
  return CUSTOMERS.find((c) => c.customer_id === id);
}
