import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, User, Info } from "lucide-react";
import { useApp } from "@/context/AppContext";
import type { ChatMessage } from "@/lib/types";
import { cn, formatTime } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const QUICK_REPLIES = [
  "Yes please",
  "Not interested",
  "Call me tomorrow",
  "What's the price?",
  "Thank you for contacting us! Our team will respond shortly.",
];

export function ChatInterface() {
  const { activeSession, sendMerchantReply, isLoading, selectedMerchant } = useApp();
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeSession?.messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const msg = input.trim();
    setInput("");
    await sendMerchantReply(msg);
  };

  if (!selectedMerchant) {
    return (
      <Card className="h-[min(70vh,600px)] flex flex-col border-dashed">
        <CardContent className="flex-1 flex flex-col items-center justify-center text-center p-8">
          <div className="h-16 w-16 rounded-2xl bg-vera-muted flex items-center justify-center mb-4">
            <Sparkles className="h-8 w-8 text-vera" />
          </div>
          <h3 className="text-lg font-semibold mb-1">Welcome to Vera</h3>
          <p className="text-sm text-muted-foreground max-w-sm">
            Select a merchant from the dashboard, load contexts, fire a trigger, and start
            conversing as the merchant.
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!activeSession) {
    return (
      <Card className="h-[min(70vh,600px)] flex flex-col">
        <CardHeader className="border-b pb-4">
          <CardTitle className="text-base">{selectedMerchant.identity.name}</CardTitle>
          <p className="text-xs text-muted-foreground">Waiting for a trigger to start conversation</p>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col items-center justify-center gap-3">
          <Skeleton className="h-12 w-3/4 max-w-md rounded-2xl rounded-bl-sm" />
          <p className="text-sm text-muted-foreground">Fire a trigger to receive Vera&apos;s message</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-[min(70vh,600px)] flex flex-col overflow-hidden shadow-premium">
      <CardHeader className="border-b py-3 px-4 shrink-0 bg-card">
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-3 min-w-0">
            <div className="h-9 w-9 rounded-full bg-vera flex items-center justify-center shrink-0">
              <Sparkles className="h-4 w-4 text-white" />
            </div>
            <div className="min-w-0">
              <CardTitle className="text-sm truncate">Vera → {activeSession.merchantName}</CardTitle>
              <p className="text-[10px] text-muted-foreground truncate">
                {activeSession.triggerKind.replace(/_/g, " ")} · {activeSession.id}
              </p>
            </div>
          </div>
          <Badge
            variant={
              activeSession.status === "active"
                ? "success"
                : activeSession.status === "ended"
                  ? "muted"
                  : "warning"
            }
          >
            {activeSession.status}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="flex-1 overflow-y-auto p-4 space-y-3 bg-[hsl(220_14%_98%)]">
        <AnimatePresence initial={false}>
          {activeSession.messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
        </AnimatePresence>
        {isLoading && (
          <div className="flex gap-2 items-center text-xs text-muted-foreground">
            <span className="h-2 w-2 rounded-full bg-vera animate-pulse" />
            Vera is typing…
          </div>
        )}
        <div ref={bottomRef} />
      </CardContent>

      <div className="border-t p-3 space-y-2 shrink-0 bg-card">
        <div className="flex flex-wrap gap-1.5">
          {QUICK_REPLIES.map((q) => (
            <button
              key={q}
              onClick={() => setInput(q)}
              className="text-[10px] px-2 py-1 rounded-full border bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground transition-colors truncate max-w-[140px]"
            >
              {q.slice(0, 28)}
              {q.length > 28 ? "…" : ""}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Reply as merchant…"
            className="min-h-[44px] max-h-24"
            disabled={activeSession.status === "ended" || isLoading}
          />
          <Button
            variant="vera"
            size="icon"
            className="shrink-0 h-11 w-11"
            onClick={handleSend}
            disabled={!input.trim() || activeSession.status === "ended" || isLoading}
            loading={isLoading}
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </Card>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isVera = message.role === "vera";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 4 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-center"
      >
        <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground bg-muted/80 px-3 py-1.5 rounded-full max-w-[90%]">
          <Info className="h-3 w-3 shrink-0" />
          <span>{message.content}</span>
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={cn("flex gap-2", isVera ? "justify-start" : "justify-end")}
    >
      {isVera && (
        <div className="h-7 w-7 rounded-full bg-vera flex items-center justify-center shrink-0 mt-1">
          <Sparkles className="h-3.5 w-3.5 text-white" />
        </div>
      )}
      <div
        className={cn(
          "max-w-[85%] sm:max-w-[75%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed shadow-card",
          isVera
            ? "bg-white border rounded-bl-md text-foreground"
            : "bg-vera text-white rounded-br-md",
        )}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        <div
          className={cn(
            "flex items-center gap-2 mt-1.5 text-[10px]",
            isVera ? "text-muted-foreground" : "text-white/70",
          )}
        >
          <span>{formatTime(message.timestamp)}</span>
          {message.meta?.cta && <Badge variant="outline" className="text-[9px] h-4">{message.meta.cta}</Badge>}
        </div>
      </div>
      {!isVera && (
        <div className="h-7 w-7 rounded-full bg-muted flex items-center justify-center shrink-0 mt-1">
          <User className="h-3.5 w-3.5 text-muted-foreground" />
        </div>
      )}
    </motion.div>
  );
}
