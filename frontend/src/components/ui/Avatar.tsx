import { cn } from "@/lib/cn";

interface AvatarProps {
  name?: string | null;
  className?: string;
}

export function Avatar({ name, className }: AvatarProps) {
  const initial = (name?.trim()?.[0] ?? "?").toUpperCase();
  return (
    <span
      className={cn(
        "inline-flex h-8 w-8 items-center justify-center rounded-full bg-[var(--primary)]/15 text-sm font-medium text-[var(--primary)]",
        className,
      )}
    >
      {initial}
    </span>
  );
}
