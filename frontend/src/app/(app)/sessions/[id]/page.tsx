"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AgentStepCard } from "@/components/research/AgentStepCard";
import { AnswerPanel } from "@/components/research/AnswerPanel";
import { Card } from "@/components/ui/Card";
import { Spinner } from "@/components/ui/Spinner";
import { api } from "@/lib/api";
import { formatRelative } from "@/lib/format";
import type { ResearchSession } from "@/lib/types";

export default function SessionDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;
  const [session, setSession] = useState<ResearchSession | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api.sessions
      .get(id)
      .then(setSession)
      .catch((e: Error) => setError(e.message));
  }, [id]);

  if (error) {
    return (
      <div className="mx-auto max-w-3xl px-6 py-8">
        <Card className="text-sm text-[var(--danger)]">{error}</Card>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="flex justify-center py-12">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-8">
      <div>
        <Link href="/sessions" className="text-xs text-[var(--muted)] hover:underline">
          ← Sessions
        </Link>
        <h1 className="mt-2 text-xl font-semibold">{session.query}</h1>
        <p className="mt-1 text-xs text-[var(--muted)]">
          {formatRelative(session.createdAt)}
          {typeof session.score === "number" && ` • score ${session.score}/10`}
        </p>
      </div>

      <AnswerPanel answer={session.answer ?? ""} score={session.score} streaming={false} />

      <div className="flex flex-col gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-[var(--muted)]">
          Agent trace
        </h2>
        <div className="flex flex-col gap-2">
          {session.steps.map((step) => (
            <AgentStepCard key={step.id} step={step} />
          ))}
        </div>
      </div>
    </div>
  );
}
