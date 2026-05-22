"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";

const items = [
  { href: "/research", label: "Research", icon: "✦" },
  { href: "/sessions", label: "Sessions", icon: "❍" },
];

export function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="flex w-56 flex-col border-r border-[var(--border)] bg-[var(--surface)] p-3">
      <Link href="/research" className="mb-6 flex items-center gap-2 px-2 py-1 font-semibold">
        <span className="inline-block h-6 w-6 rounded-md bg-[var(--primary)]" />
        AgentForge
      </Link>
      <nav className="flex flex-col gap-1">
        {items.map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm transition-colors",
                active
                  ? "bg-[var(--surface-2)] font-medium text-[var(--foreground)]"
                  : "text-[var(--muted)] hover:bg-[var(--surface-2)] hover:text-[var(--foreground)]",
              )}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
