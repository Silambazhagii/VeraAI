import { motion } from "framer-motion";
import { Zap, Clock, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { useApp } from "@/context/AppContext";
import { getTriggersForMerchant, TRIGGER_KINDS } from "@/data/seed";
import type { Trigger } from "@/lib/types";
import { triggerKindLabel } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface TriggerSimulatorProps {
  onFired?: () => void;
}

export function TriggerSimulator({ onFired }: TriggerSimulatorProps) {
  const { selectedMerchant, contextsLoaded, loadMerchantContexts, fireTrigger, isLoading } =
    useApp();

  const triggers = selectedMerchant
    ? getTriggersForMerchant(selectedMerchant.merchant_id)
    : [];

  const handleLoadContexts = async () => {
    if (!selectedMerchant) return;
    try {
      await loadMerchantContexts(selectedMerchant);
    } catch {
      /* toast handled in context */
    }
  };

  const handleFire = async (trigger: Trigger) => {
    if (!contextsLoaded) {
      toast.error("Load merchant contexts first");
      return;
    }
    await fireTrigger(trigger);
    onFired?.();
  };

  if (!selectedMerchant) {
    return (
      <Card className="border-dashed">
        <CardContent className="py-10 text-center">
          <Zap className="h-8 w-8 text-muted-foreground/40 mx-auto mb-2" />
          <p className="text-sm text-muted-foreground">Select a merchant to simulate triggers</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Zap className="h-4 w-4 text-vera" />
          Trigger Simulator
        </CardTitle>
        <CardDescription>
          Push contexts and fire triggers via <code className="text-xs">POST /v1/tick</code>
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!contextsLoaded ? (
          <Button
            variant="vera"
            className="w-full"
            onClick={handleLoadContexts}
            loading={isLoading}
          >
            Load Merchant Contexts
          </Button>
        ) : (
          <Badge variant="success" className="w-full justify-center py-1.5">
            Contexts loaded on backend
          </Badge>
        )}

        <div className="flex flex-wrap gap-1.5">
          {TRIGGER_KINDS.map((k) => (
            <Badge key={k} variant="muted" className="text-[10px]">
              {triggerKindLabel(k)}
            </Badge>
          ))}
        </div>

        <div className="space-y-2 max-h-[320px] overflow-y-auto pr-1">
          {triggers.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No triggers for this merchant
            </p>
          ) : (
            triggers.map((trigger, i) => (
              <motion.div
                key={trigger.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className="group flex items-center gap-3 rounded-lg border bg-card p-3 hover:border-vera/30 hover:shadow-card transition-all"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {triggerKindLabel(trigger.kind)}
                  </p>
                  <div className="flex items-center gap-2 mt-0.5">
                    <Badge variant="outline" className="text-[10px] capitalize">
                      {trigger.scope}
                    </Badge>
                    <span className="flex items-center gap-0.5 text-[10px] text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      urgency {trigger.urgency}
                    </span>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={!contextsLoaded || isLoading}
                  onClick={() => handleFire(trigger)}
                  className="shrink-0 group-hover:border-vera group-hover:text-vera"
                >
                  Fire
                  <ArrowRight className="h-3 w-3" />
                </Button>
              </motion.div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
