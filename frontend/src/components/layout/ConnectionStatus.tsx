import { motion } from "framer-motion";
import { Activity, Wifi, WifiOff } from "lucide-react";
import { useHealth } from "@/hooks/useApi";
import { cn, formatUptime } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export function ConnectionStatus({ compact = false }: { compact?: boolean }) {
  const { data, isLoading, isError, isFetching } = useHealth();

  if (isLoading) {
    return compact ? (
      <Skeleton className="h-6 w-20 rounded-full" />
    ) : (
      <Skeleton className="h-10 w-full rounded-lg" />
    );
  }

  const online = !isError && data?.status === "ok";

  return (
    <motion.div
      initial={{ opacity: 0, y: -4 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn(
        "flex items-center gap-2",
        compact ? "" : "rounded-lg border bg-card px-3 py-2 shadow-card",
      )}
    >
      {online ? (
        <Wifi className="h-3.5 w-3.5 text-success" />
      ) : (
        <WifiOff className="h-3.5 w-3.5 text-destructive" />
      )}
      <Badge variant={online ? "success" : "destructive"} className="text-[10px]">
        {online ? "Connected" : "Offline"}
      </Badge>
      {!compact && data && (
        <span className="ml-auto flex items-center gap-1 text-xs text-muted-foreground">
          <Activity className="h-3 w-3" />
          {formatUptime(data.uptime_seconds)}
          {isFetching && <span className="animate-pulse">·</span>}
        </span>
      )}
    </motion.div>
  );
}

export function ContextCounts() {
  const { data, isLoading } = useHealth();

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-4 gap-2">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-14 rounded-lg" />
        ))}
      </div>
    );
  }

  const items = [
    { label: "Categories", value: data.contexts_loaded.category },
    { label: "Merchants", value: data.contexts_loaded.merchant },
    { label: "Customers", value: data.contexts_loaded.customer },
    { label: "Triggers", value: data.contexts_loaded.trigger },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {items.map((item, i) => (
        <motion.div
          key={item.label}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
          className="rounded-lg border bg-card p-3 text-center shadow-card"
        >
          <p className="text-2xl font-semibold tabular-nums">{item.value}</p>
          <p className="text-xs text-muted-foreground mt-0.5">{item.label}</p>
        </motion.div>
      ))}
    </div>
  );
}
