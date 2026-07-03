import { motion } from "framer-motion";
import { MessageSquare, Clock } from "lucide-react";
import { useApp } from "@/context/AppContext";
import { triggerKindLabel } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export function ConversationHistory() {
  const { sessions, activeSession } = useApp();

  if (sessions.length === 0) {
    return (
      <Card className="border-dashed">
        <CardContent className="py-8 text-center">
          <MessageSquare className="h-8 w-8 text-muted-foreground/40 mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">No conversations yet</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Clock className="h-4 w-4" />
          History
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-[280px] overflow-y-auto">
        {sessions.map((session, i) => (
          <motion.button
            key={session.id}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.03 }}
            onClick={() => {
              /* view-only history list */
            }}
            className={`w-full text-left rounded-lg border p-3 transition-all hover:shadow-card ${
              activeSession?.id === session.id
                ? "border-vera/40 bg-vera-muted/30"
                : "hover:border-border"
            }`}
          >
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium truncate">{session.merchantName}</p>
              <Badge variant="outline" className="text-[10px] shrink-0">
                {session.status}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground mt-0.5">
              {triggerKindLabel(session.triggerKind)} · {session.messages.length} msgs
            </p>
            <p className="text-xs text-muted-foreground/70 truncate mt-1">
              {session.messages[session.messages.length - 1]?.content.slice(0, 60)}…
            </p>
          </motion.button>
        ))}
      </CardContent>
    </Card>
  );
}
