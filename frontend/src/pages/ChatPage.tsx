import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { MERCHANTS } from "@/data/seed";
import { ChatInterface } from "@/components/chat/ChatInterface";
import { ConversationHistory } from "@/components/chat/ConversationHistory";
import { MerchantContextPanel } from "@/components/context/MerchantContextPanel";
import { TriggerSimulator } from "@/components/triggers/TriggerSimulator";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

export function ChatPage() {
  const { selectedMerchant, setSelectedMerchant, isLoading } = useApp();

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <Link to="/">
            <Button variant="ghost" size="sm" className="-ml-2 mb-1">
              <ArrowLeft className="h-4 w-4" />
              Dashboard
            </Button>
          </Link>
          <motion.h1
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-2xl font-bold tracking-tight"
          >
            Vera Chat
          </motion.h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Simulate merchant ↔ Vera conversations via the live API
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {MERCHANTS.map((m) => (
            <button
              key={m.merchant_id}
              onClick={() => setSelectedMerchant(m)}
              className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${
                selectedMerchant?.merchant_id === m.merchant_id
                  ? "bg-vera text-white border-vera"
                  : "hover:bg-muted"
              }`}
            >
              {m.identity.owner_first_name ?? m.identity.name.split(" ")[0]}
            </button>
          ))}
        </div>
      </div>

      {selectedMerchant && (
        <Badge variant="secondary" className="capitalize">
          {selectedMerchant.identity.name} · {selectedMerchant.category_slug}
        </Badge>
      )}

      <div className="grid gap-4 lg:grid-cols-12">
        <motion.div
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          className="lg:col-span-7 xl:col-span-8"
        >
          <ChatInterface />
        </motion.div>

        <div className="lg:col-span-5 xl:col-span-4 space-y-4">
          <TriggerSimulator />
          <MerchantContextPanel merchant={selectedMerchant} loading={isLoading} />
          <ConversationHistory />
        </div>
      </div>
    </div>
  );
}
