import { motion } from "framer-motion";
import {
  Building2,
  MapPin,
  TrendingUp,
  CreditCard,
  AlertCircle,
  Tag,
  Users,
} from "lucide-react";
import type { Merchant } from "@/lib/types";
import { cn, formatCtr } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

interface MerchantContextPanelProps {
  merchant: Merchant | null;
  loading?: boolean;
}

export function MerchantContextPanel({ merchant, loading }: MerchantContextPanelProps) {
  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-5 w-40" />
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-24 w-full" />
        </CardContent>
      </Card>
    );
  }

  if (!merchant) {
    return (
      <Card className="border-dashed">
        <CardContent className="flex flex-col items-center justify-center py-12 text-center">
          <Building2 className="h-10 w-10 text-muted-foreground/40 mb-3" />
          <p className="text-sm font-medium text-muted-foreground">No merchant selected</p>
          <p className="text-xs text-muted-foreground/70 mt-1 max-w-[200px]">
            Choose a merchant to view context, performance, and signals
          </p>
        </CardContent>
      </Card>
    );
  }

  const activeOffers = merchant.offers.filter((o) => o.status === "active");

  return (
    <Card className="overflow-hidden">
      <CardHeader className="pb-3 bg-gradient-to-br from-vera-muted/50 to-transparent">
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle className="text-base leading-snug">{merchant.identity.name}</CardTitle>
            <div className="flex items-center gap-1.5 mt-1 text-xs text-muted-foreground">
              <MapPin className="h-3 w-3" />
              {merchant.identity.locality}, {merchant.identity.city}
            </div>
          </div>
          <Badge variant={merchant.identity.verified ? "success" : "warning"}>
            {merchant.identity.verified ? "Verified" : "Unverified"}
          </Badge>
        </div>
        <Badge variant="secondary" className="w-fit mt-2 capitalize">
          {merchant.category_slug}
        </Badge>
      </CardHeader>

      <CardContent className="space-y-4 pt-4">
        <Section icon={CreditCard} title="Subscription">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Plan</span>
            <span className="font-medium">{merchant.subscription.plan ?? "—"}</span>
          </div>
          <div className="flex justify-between text-sm mt-1">
            <span className="text-muted-foreground">Status</span>
            <span className="font-medium capitalize">{merchant.subscription.status}</span>
          </div>
          {merchant.subscription.days_remaining != null && (
            <div className="flex justify-between text-sm mt-1">
              <span className="text-muted-foreground">Days left</span>
              <span
                className={cn(
                  "font-medium",
                  merchant.subscription.days_remaining <= 14 && "text-amber-600",
                )}
              >
                {merchant.subscription.days_remaining}
              </span>
            </div>
          )}
        </Section>

        <Section icon={TrendingUp} title="Performance (30d)">
          <div className="grid grid-cols-3 gap-2">
            <Metric label="Views" value={merchant.performance.views?.toLocaleString() ?? "—"} />
            <Metric label="Calls" value={merchant.performance.calls?.toString() ?? "—"} />
            <Metric
              label="CTR"
              value={merchant.performance.ctr != null ? formatCtr(merchant.performance.ctr) : "—"}
            />
          </div>
        </Section>

        {activeOffers.length > 0 && (
          <Section icon={Tag} title="Active Offers">
            <div className="space-y-1.5">
              {activeOffers.map((o) => (
                <p key={o.id} className="text-sm font-medium text-foreground/90">
                  {o.title}
                </p>
              ))}
            </div>
          </Section>
        )}

        {merchant.signals.length > 0 && (
          <Section icon={AlertCircle} title="Signals">
            <div className="flex flex-wrap gap-1.5">
              {merchant.signals.map((s) => (
                <Badge key={s} variant="outline" className="text-[10px] font-normal">
                  {s.replace(/_/g, " ")}
                </Badge>
              ))}
            </div>
          </Section>
        )}

        {merchant.customer_aggregate && (
          <Section icon={Users} title="Customers">
            <div className="grid grid-cols-2 gap-2 text-sm">
              {Object.entries(merchant.customer_aggregate).slice(0, 4).map(([k, v]) => (
                <div key={k}>
                  <p className="text-muted-foreground text-xs">{k.replace(/_/g, " ")}</p>
                  <p className="font-medium tabular-nums">
                    {typeof v === "number" && v < 1 ? `${(v * 100).toFixed(0)}%` : v}
                  </p>
                </div>
              ))}
            </div>
          </Section>
        )}
      </CardContent>
    </Card>
  );
}

function Section({
  icon: Icon,
  title,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div className="flex items-center gap-2 mb-2">
        <Icon className="h-3.5 w-3.5 text-muted-foreground" />
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </p>
      </div>
      {children}
    </motion.div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg bg-muted/50 px-2 py-2 text-center">
      <p className="text-sm font-semibold tabular-nums">{value}</p>
      <p className="text-[10px] text-muted-foreground">{label}</p>
    </div>
  );
}
