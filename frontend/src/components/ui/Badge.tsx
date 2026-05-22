import type { HTMLAttributes } from "react";
import { cn } from "@/lib/cn";
import type { AgentRole } from "@/lib/types";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: "default" | "primary" | "success" | "warning" | "danger" | AgentRole;
}

const tones: Record<string, string> = {
  default: "bg-[var(--surface-2)] text-[var(--foreground)]",
  primary: "bg-[var(--primary)]/15 text-[var(--primary)]",
  success: "bg-[var(--success)]/15 text-[var(--success)]",
  warning: "bg-[var(--warning)]/15 text-[var(--warning)]",
  danger: "bg-[var(--danger)]/15 text-[var(--danger)]",
  planner: "bg-[var(--planner)]/15 text-[var(--planner)]",
  researcher: "bg-[var(--researcher)]/15 text-[var(--researcher)]",
  synthesizer: "bg-[var(--synthesizer)]/15 text-[var(--synthesizer)]",
  critic: "bg-[var(--critic)]/15 text-[var(--critic)]",
};

export function Badge({ className, tone = "default", ...rest }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium",
        tones[tone],
        className,
      )}
      {...rest}
    />
  );
}
