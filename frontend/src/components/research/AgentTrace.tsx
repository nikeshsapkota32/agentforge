import type { AgentStep, SSEEvent } from "@/lib/types";
import { AgentStepCard } from "./AgentStepCard";

export function AgentTrace({ events }: { events: SSEEvent[] }) {
  const steps = buildSteps(events);
  if (steps.length === 0) return null;
  return (
    <div className="flex flex-col gap-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
        Agent trace
      </h2>
      <div className="flex flex-col gap-2">
        {steps.map((step) => (
          <AgentStepCard key={step.id} step={step} />
        ))}
      </div>
    </div>
  );
}

function buildSteps(events: SSEEvent[]): AgentStep[] {
  const map = new Map<string, AgentStep>();
  for (const evt of events) {
    if (evt.type === "agent_step") {
      const existing = map.get(evt.step.id);
      map.set(evt.step.id, existing ? { ...existing, ...evt.step } : evt.step);
    } else if (evt.type === "tool_call") {
      const step = map.get(evt.stepId);
      if (step) {
        const i = step.toolCalls.findIndex((c) => c.id === evt.call.id);
        if (i === -1) step.toolCalls.push(evt.call);
        else step.toolCalls[i] = evt.call;
      }
    }
  }
  return Array.from(map.values()).sort((a, b) => a.startedAt.localeCompare(b.startedAt));
}
