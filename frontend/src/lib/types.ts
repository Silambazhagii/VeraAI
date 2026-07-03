export interface HealthResponse {
  status: string;
  uptime_seconds: number;
  contexts_loaded: {
    category: number;
    merchant: number;
    customer: number;
    trigger: number;
  };
}

export interface MetadataResponse {
  team_name: string;
  model: string;
  approach: string;
  version: string;
  contact_email: string;
}

export interface ContextPushResponse {
  accepted: boolean;
  ack_id?: string;
  stored_at?: string;
  reason?: string;
  current_version?: number;
}

export interface TickAction {
  conversation_id: string;
  merchant_id: string;
  customer_id: string | null;
  send_as: "vera" | "merchant_on_behalf";
  trigger_id: string;
  template_name: string;
  template_params: string[];
  body: string;
  cta: string;
  suppression_key: string;
  rationale: string;
}

export interface TickResponse {
  actions: TickAction[];
}

export interface ReplyResponse {
  action: "send" | "wait" | "end";
  body?: string;
  cta?: string;
  wait_seconds?: number;
  rationale: string;
}

export interface ChatMessage {
  id: string;
  role: "vera" | "merchant" | "system";
  content: string;
  timestamp: Date;
  meta?: {
    trigger_id?: string;
    cta?: string;
    rationale?: string;
    action?: string;
  };
}

export interface ConversationSession {
  id: string;
  merchantId: string;
  merchantName: string;
  triggerId: string;
  triggerKind: string;
  turnNumber: number;
  messages: ChatMessage[];
  status: "active" | "ended" | "waiting";
}

export interface Merchant {
  merchant_id: string;
  category_slug: string;
  identity: {
    name: string;
    city: string;
    locality: string;
    owner_first_name?: string;
    verified?: boolean;
    languages?: string[];
  };
  subscription: {
    status: string;
    plan?: string;
    days_remaining?: number;
  };
  performance: {
    views?: number;
    calls?: number;
    ctr?: number;
    directions?: number;
    delta_7d?: Record<string, number>;
  };
  offers: Array<{ id: string; title: string; status: string }>;
  signals: string[];
  customer_aggregate?: Record<string, number>;
  conversation_history?: Array<{ ts: string; from: string; body: string }>;
}

export interface Trigger {
  id: string;
  scope: string;
  kind: string;
  source?: string;
  merchant_id: string;
  customer_id: string | null;
  payload: Record<string, unknown>;
  urgency: number;
  suppression_key: string;
  expires_at?: string;
}

export interface Category {
  slug: string;
  display_name?: string;
  voice?: Record<string, unknown>;
  peer_stats?: Record<string, number>;
  digest?: Array<Record<string, unknown>>;
}

export interface Customer {
  customer_id: string;
  merchant_id: string;
  identity: { name: string; language_pref?: string };
  relationship?: Record<string, unknown>;
  state?: string;
  consent?: { scope?: string[] };
}
