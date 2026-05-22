import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import type { AgentStep } from "@/lib/types";
import { ToolCallBadge } from "./ToolCallBadge";

const roleLabel = {
  planner: "Planner",
  researcher: "Researcher",
  synthesizer: "Synthesizer",
  critic: "Critic",
} as const;

export function AgentStepCard({ step }: { step: AgentStep }) {
  const isLive = !step.endedAt;
  return (
    <Card className="flex flex-col gap-2">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Badge tone={step.role}>{roleLabel[step.role]}</Badge>
          {isLive && (
            <span className="flex items-center gap-1 text-xs text-[var(--muted)]">
              <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-[var(--primary)]" />
              thinking
            </span>
          )}
        </div>
        {typeof step.tokensIn === "number" && typeof step.tokensOut === "number" && (
          <span className="font-mono text-xs text-[var(--muted)]">
            {step.tokensIn}↓ {step.tokensOut}↑
          </span>
        )}
      </div>
      {step.thought && (
        <p className="whitespace-pre-wrap text-sm text-[var(--foreground)]/90">{step.thought}</p>
      )}
      {step.toolCalls.length > 0 && (
        <div className="flex flex-wrap gap-1.5 pt-1">
          {step.toolCalls.map((c) => (
            <ToolCallBadge key={c.id} call={c} />
          ))}
        </div>
      )}
    </Card>
  );
}
