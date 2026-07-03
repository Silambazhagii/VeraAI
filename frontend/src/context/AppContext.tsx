import { createContext, useContext, useState, useCallback, type ReactNode } from "react";
import { toast } from "sonner";
import { api, ApiError } from "@/lib/api";
import type { ChatMessage, ConversationSession, Merchant, Trigger } from "@/lib/types";
import { utcNowIso } from "@/lib/utils";
import {
  getCategory,
  getCustomer,
  getTriggersForMerchant,
} from "@/data/seed";

interface AppContextValue {
  selectedMerchant: Merchant | null;
  setSelectedMerchant: (m: Merchant | null) => void;
  activeSession: ConversationSession | null;
  sessions: ConversationSession[];
  contextsLoaded: boolean;
  loadMerchantContexts: (merchant: Merchant) => Promise<void>;
  fireTrigger: (trigger: Trigger) => Promise<void>;
  sendMerchantReply: (message: string) => Promise<void>;
  isLoading: boolean;
}

const AppContext = createContext<AppContextValue | null>(null);

function msgId() {
  return `msg_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

export function AppProvider({ children }: { children: ReactNode }) {
  const [selectedMerchant, setSelectedMerchant] = useState<Merchant | null>(null);
  const [activeSession, setActiveSession] = useState<ConversationSession | null>(null);
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [contextsLoaded, setContextsLoaded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const loadMerchantContexts = useCallback(async (merchant: Merchant) => {
    setIsLoading(true);
    try {
      const category = getCategory(merchant.category_slug);
      if (category) {
        await api.pushContext({
          scope: "category",
          context_id: category.slug,
          version: 1,
          payload: category as unknown as Record<string, unknown>,
          delivered_at: utcNowIso(),
        });
      }
      await api.pushContext({
        scope: "merchant",
        context_id: merchant.merchant_id,
        version: 1,
        payload: merchant as unknown as Record<string, unknown>,
        delivered_at: utcNowIso(),
      });
      const triggers = getTriggersForMerchant(merchant.merchant_id);
      for (const trigger of triggers) {
        await api.pushContext({
          scope: "trigger",
          context_id: trigger.id,
          version: 1,
          payload: trigger as unknown as Record<string, unknown>,
          delivered_at: utcNowIso(),
        });
        if (trigger.customer_id) {
          const customer = getCustomer(trigger.customer_id);
          if (customer) {
            await api.pushContext({
              scope: "customer",
              context_id: customer.customer_id,
              version: 1,
              payload: customer as unknown as Record<string, unknown>,
              delivered_at: utcNowIso(),
            });
          }
        }
      }
      setContextsLoaded(true);
      toast.success(`Contexts loaded for ${merchant.identity.name}`);
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Failed to load contexts";
      toast.error(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fireTrigger = useCallback(
    async (trigger: Trigger) => {
      if (!selectedMerchant) return;
      setIsLoading(true);
      try {
        const tick = await api.tick({
          now: utcNowIso(),
          available_triggers: [trigger.id],
        });

        if (tick.actions.length === 0) {
          toast.info("Bot chose not to send for this trigger");
          return;
        }

        const action = tick.actions[0];
        const veraMessage: ChatMessage = {
          id: msgId(),
          role: "vera",
          content: action.body,
          timestamp: new Date(),
          meta: {
            trigger_id: action.trigger_id,
            cta: action.cta,
            rationale: action.rationale,
          },
        };

        const session: ConversationSession = {
          id: action.conversation_id,
          merchantId: action.merchant_id,
          merchantName: selectedMerchant.identity.name,
          triggerId: action.trigger_id,
          triggerKind: trigger.kind,
          turnNumber: 1,
          messages: [veraMessage],
          status: "active",
        };

        setActiveSession(session);
        setSessions((prev) => [session, ...prev.filter((s) => s.id !== session.id)]);
        toast.success("Vera sent a proactive message");
      } catch (err) {
        const message = err instanceof ApiError ? err.message : "Tick failed";
        toast.error(message);
      } finally {
        setIsLoading(false);
      }
    },
    [selectedMerchant],
  );

  const sendMerchantReply = useCallback(
    async (message: string) => {
      if (!activeSession || !selectedMerchant) return;
      setIsLoading(true);

      const merchantMsg: ChatMessage = {
        id: msgId(),
        role: "merchant",
        content: message,
        timestamp: new Date(),
      };

      const turnNumber = activeSession.turnNumber + 1;
      const updatedMessages = [...activeSession.messages, merchantMsg];

      setActiveSession((s) =>
        s ? { ...s, messages: updatedMessages, turnNumber } : s,
      );

      try {
        const response = await api.reply({
          conversation_id: activeSession.id,
          merchant_id: selectedMerchant.merchant_id,
          customer_id: null,
          from_role: "merchant",
          message,
          received_at: utcNowIso(),
          turn_number: turnNumber,
        });

        let newMessages = [...updatedMessages];
        let status: ConversationSession["status"] = "active";

        if (response.action === "send" && response.body) {
          newMessages.push({
            id: msgId(),
            role: "vera",
            content: response.body,
            timestamp: new Date(),
            meta: { cta: response.cta, rationale: response.rationale, action: response.action },
          });
        } else if (response.action === "wait") {
          newMessages.push({
            id: msgId(),
            role: "system",
            content: `Vera is waiting ${response.wait_seconds ?? 0}s — ${response.rationale}`,
            timestamp: new Date(),
          });
          status = "waiting";
        } else if (response.action === "end") {
          newMessages.push({
            id: msgId(),
            role: "system",
            content: `Conversation ended — ${response.rationale}`,
            timestamp: new Date(),
          });
          status = "ended";
        }

        const updated: ConversationSession = {
          ...activeSession,
          messages: newMessages,
          turnNumber,
          status,
        };
        setActiveSession(updated);
        setSessions((prev) => prev.map((s) => (s.id === updated.id ? updated : s)));
      } catch (err) {
        const msg = err instanceof ApiError ? err.message : "Reply failed";
        toast.error(msg);
      } finally {
        setIsLoading(false);
      }
    },
    [activeSession, selectedMerchant],
  );

  return (
    <AppContext.Provider
      value={{
        selectedMerchant,
        setSelectedMerchant: (m) => {
          setSelectedMerchant(m);
          setContextsLoaded(false);
          setActiveSession(null);
        },
        activeSession,
        sessions,
        contextsLoaded,
        loadMerchantContexts,
        fireTrigger,
        sendMerchantReply,
        isLoading,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
