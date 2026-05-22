"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Avatar } from "@/components/ui/Avatar";
import { Button } from "@/components/ui/Button";
import { api } from "@/lib/api";
import { clearTokens, decodeJwt, getAccessToken } from "@/lib/auth";

export function Header() {
  const router = useRouter();
  const [email, setEmail] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;
    const payload = decodeJwt(token);
    if (payload?.email) setEmail(payload.email);
  }, []);

  async function logout() {
    try {
      await api.auth.logout();
    } catch {
      // proceed regardless
    }
    clearTokens();
    router.push("/login");
  }

  return (
    <header className="flex h-14 items-center justify-end border-b border-[var(--border)] bg-[var(--background)] px-4">
      <div className="relative">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          className="flex items-center gap-2 rounded-md px-2 py-1 text-sm hover:bg-[var(--surface-2)]"
        >
          <Avatar name={email} />
          <span className="hidden text-[var(--muted)] sm:inline">{email ?? "Account"}</span>
        </button>
        {open && (
          <div className="absolute right-0 top-full mt-1 w-48 rounded-md border border-[var(--border)] bg-[var(--surface)] p-1 shadow-md">
            <Button variant="ghost" size="sm" className="w-full justify-start" onClick={logout}>
              Sign out
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
