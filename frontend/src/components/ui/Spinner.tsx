import { cn } from "@/lib/cn";

interface SpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizes = {
  sm: "h-3.5 w-3.5 border-2",
  md: "h-5 w-5 border-2",
  lg: "h-8 w-8 border-[3px]",
};

export function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <span
      aria-label="Loading"
      className={cn(
        "inline-block animate-spin rounded-full border-current border-r-transparent text-[var(--muted)]",
        sizes[size],
        className,
      )}
    />
  );
}
