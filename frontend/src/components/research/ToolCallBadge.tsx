import { Badge } from "@/components/ui/Badge";
import type { ToolCall } from "@/lib/types";

const labels: Record<string, string> = {
  web_search: "Web search",
  web_fetch: "Web fetch",
  wikipedia: "Wikipedia",
  arxiv: "arXiv",
  pdf_read: "PDF",
  python_exec: "Python",
  calculator: "Calc",
  vector_search: "Memory search",
  vector_write: "Memory write",
  summarize: "Summarize",
  translate: "Translate",
  datetime: "Datetime",
};

export function ToolCallBadge({ call }: { call: ToolCall }) {
  const label = labels[call.tool] ?? call.tool;
  const tone = call.error ? "danger" : "primary";
  return (
    <Badge tone={tone} title={call.error ?? undefined}>
      <span className="font-mono text-[10px]">⚙</span> {label}
      {typeof call.durationMs === "number" && (
        <span className="text-[var(--muted)]">{call.durationMs}ms</span>
      )}
    </Badge>
  );
}
