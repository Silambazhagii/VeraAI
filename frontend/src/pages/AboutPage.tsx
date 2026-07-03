import { motion } from "framer-motion";
import { Mail, Github, Cpu, Layers, Zap } from "lucide-react";
import { useMetadata } from "@/hooks/useApi";
import { ConnectionStatus, ContextCounts } from "@/components/layout/ConnectionStatus";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const endpoints = [
  { method: "GET", path: "/v1/healthz", desc: "Liveness + context counts" },
  { method: "GET", path: "/v1/metadata", desc: "Bot identity & approach" },
  { method: "POST", path: "/v1/context", desc: "Push category/merchant/customer/trigger" },
  { method: "POST", path: "/v1/tick", desc: "Proactive message decisions" },
  { method: "POST", path: "/v1/reply", desc: "Multi-turn conversation replies" },
];

export function AboutPage() {
  const { data: meta, isLoading } = useMetadata();

  return (
    <div className="max-w-3xl mx-auto space-y-8">
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
        <Badge variant="secondary" className="mb-3">About Vera</Badge>
        <h1 className="text-3xl font-bold tracking-tight">Magicpin AI Merchant Assistant</h1>
        <p className="mt-3 text-muted-foreground leading-relaxed">
          Vera is a context-aware AI backend that engages merchants on WhatsApp. This frontend
          connects to the live FastAPI backend — no mocks — for demo and development.
        </p>
      </motion.div>

      <ConnectionStatus />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Cpu className="h-4 w-4" />
            Metadata
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : meta ? (
            <dl className="grid gap-2 text-sm">
              <Row label="Team" value={meta.team_name} />
              <Row label="Model" value={meta.model} />
              <Row label="Approach" value={meta.approach} />
              <Row label="Version" value={meta.version} />
              <Row label="Contact" value={meta.contact_email} icon={<Mail className="h-3.5 w-3.5" />} />
            </dl>
          ) : (
            <p className="text-sm text-destructive">Could not load metadata</p>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Layers className="h-4 w-4" />
            Loaded Contexts
          </CardTitle>
          <CardDescription>Live counts from the backend store</CardDescription>
        </CardHeader>
        <CardContent>
          <ContextCounts />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Zap className="h-4 w-4" />
            API Endpoints
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {endpoints.map((ep) => (
            <div
              key={ep.path}
              className="flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm"
            >
              <Badge variant={ep.method === "GET" ? "secondary" : "default"} className="text-[10px] w-12 justify-center">
                {ep.method}
              </Badge>
              <code className="text-xs font-mono text-vera">{ep.path}</code>
              <span className="text-muted-foreground text-xs ml-auto hidden sm:inline">
                {ep.desc}
              </span>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card className="border-dashed">
        <CardContent className="py-6 text-center text-sm text-muted-foreground">
          <Github className="h-5 w-5 mx-auto mb-2 opacity-40" />
          Backend: FastAPI · Frontend: React + Vite + Tailwind
        </CardContent>
      </Card>
    </div>
  );
}

function Row({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="flex justify-between gap-4 py-1 border-b border-border/50 last:border-0">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="font-medium text-right flex items-center gap-1.5 justify-end">{icon}{value}</dd>
    </div>
  );
}
