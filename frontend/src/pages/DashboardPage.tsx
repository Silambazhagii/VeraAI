import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import {
  ArrowRight,
  MessageSquare,
  Zap,
  Shield,
  BarChart3,
  Sparkles,
} from "lucide-react";
import { MERCHANTS } from "@/data/seed";
import { useApp } from "@/context/AppContext";
import { useHealth, useMetadata } from "@/hooks/useApi";
import { ContextCounts, ConnectionStatus } from "@/components/layout/ConnectionStatus";
import { MerchantContextPanel } from "@/components/context/MerchantContextPanel";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export function DashboardPage() {
  const { selectedMerchant, setSelectedMerchant } = useApp();
  const { data: meta, isLoading: metaLoading } = useMetadata();
  const { data: health } = useHealth();

  return (
    <div className="space-y-8">
      <motion.section
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative overflow-hidden rounded-2xl border bg-card p-6 sm:p-10 shadow-premium"
      >
        <div className="absolute inset-0 bg-gradient-to-br from-vera-muted/60 via-transparent to-transparent pointer-events-none" />
        <div className="relative max-w-2xl">
          <Badge variant="secondary" className="mb-4">
            Magicpin AI Challenge
          </Badge>
          <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-balance">
            Merchant intelligence,{" "}
            <span className="text-vera">beautifully orchestrated</span>
          </h1>
          <p className="mt-3 text-muted-foreground text-base sm:text-lg leading-relaxed max-w-xl">
            Interact with Vera — context-aware AI that engages merchants on WhatsApp with
            personalized, trigger-driven conversations.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to="/chat">
              <Button variant="vera">
                Open Chat
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link to="/about">
              <Button variant="outline">Learn more</Button>
            </Link>
          </div>
        </div>
      </motion.section>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { icon: Shield, label: "API Status", value: health?.status === "ok" ? "Healthy" : "—" },
          { icon: Sparkles, label: "Model", value: metaLoading ? "…" : meta?.model?.split(" ").slice(0, 2).join(" ") },
          { icon: Zap, label: "Triggers", value: "10 kinds" },
          { icon: BarChart3, label: "Merchants", value: MERCHANTS.length.toString() },
        ].map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
          >
            <Card className="hover:shadow-elevated transition-shadow">
              <CardContent className="p-4 flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-vera-muted flex items-center justify-center">
                  <stat.icon className="h-5 w-5 text-vera" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">{stat.label}</p>
                  {metaLoading && stat.label === "Model" ? (
                    <Skeleton className="h-5 w-24 mt-0.5" />
                  ) : (
                    <p className="font-semibold text-sm">{stat.value}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Select Merchant</h2>
            <ConnectionStatus compact />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {MERCHANTS.map((merchant, i) => (
              <motion.button
                key={merchant.merchant_id}
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.04 }}
                onClick={() => setSelectedMerchant(merchant)}
                className={`text-left rounded-xl border p-4 transition-all hover:shadow-elevated focus-visible:ring-2 focus-visible:ring-ring ${
                  selectedMerchant?.merchant_id === merchant.merchant_id
                    ? "border-vera ring-1 ring-vera/20 bg-vera-muted/20"
                    : "bg-card hover:border-vera/30"
                }`}
              >
                <p className="font-semibold text-sm">{merchant.identity.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5 capitalize">
                  {merchant.category_slug} · {merchant.identity.city}
                </p>
                <div className="flex flex-wrap gap-1 mt-2">
                  {merchant.signals.slice(0, 2).map((s) => (
                    <Badge key={s} variant="muted" className="text-[9px]">
                      {s.split(":")[0].replace(/_/g, " ")}
                    </Badge>
                  ))}
                </div>
              </motion.button>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <h2 className="text-lg font-semibold">Backend Context</h2>
          <ContextCounts />
          <MerchantContextPanel merchant={selectedMerchant} />
        </div>
      </section>

      {selectedMerchant && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <Card className="bg-vera-muted/30 border-vera/20">
            <CardContent className="p-4 flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="flex items-center gap-3">
                <MessageSquare className="h-5 w-5 text-vera" />
                <p className="text-sm">
                  <span className="font-medium">{selectedMerchant.identity.name}</span> selected —
                  head to chat to fire triggers
                </p>
              </div>
              <Link to="/chat">
                <Button variant="vera" size="sm">
                  Continue to Chat
                  <ArrowRight className="h-3.5 w-3.5" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
