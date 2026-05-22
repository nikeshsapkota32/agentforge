"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { api } from "@/lib/api";
import { formatRelative } from "@/lib/format";
import type { SessionSummary } from "@/lib/types";

export default function SessionsPage() {
  const [sessions, setSessions] = useState<SessionSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.sessions
      .list()
      .then(setSessions)
      .catch((e: Error) => setError(e.message));
  }, []);

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-8">
      <div>
        <h1 className="text-2xl font-semibold">Sessions</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Your past research runs.</p>
      </div>

      {error && (
        <div className="rounded-md border border-[var(--danger)]/40 bg-[var(--danger)]/10 px-3 py-2 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}

      {sessions === null && !error && (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      )}

      {sessions && sessions.length === 0 && (
        <Card className="text-center text-sm text-[var(--muted)]">
          No sessions yet.{" "}
          <Link href="/research" className="font-medium text-[var(--primary)] hover:underline">
            Start your first one
          </Link>
          .
        </Card>
      )}

      {sessions && sessions.length > 0 && (
        <div className="flex flex-col gap-2">
          {sessions.map((s) => (
            <Link
              key={s.id}
              href={`/sessions/${s.id}`}
              className="block rounded-lg border border-[var(--border)] bg-[var(--surface)] p-4 transition-colors hover:bg-[var(--surface-2)]"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="line-clamp-2 text-sm font-medium">{s.query}</p>
                  <p className="mt-1 text-xs text-[var(--muted)]">{formatRelative(s.createdAt)}</p>
                </div>
                {typeof s.score === "number" && (
                  <Badge tone={s.score >= 8 ? "success" : s.score >= 6 ? "warning" : "danger"}>
                    {s.score}/10
                  </Badge>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
