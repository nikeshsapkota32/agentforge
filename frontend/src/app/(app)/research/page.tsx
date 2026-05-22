"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { AgentTrace } from "@/components/research/AgentTrace";
import { AnswerPanel } from "@/components/research/AnswerPanel";
import { QueryComposer } from "@/components/research/QueryComposer";
import { useResearchStream } from "@/lib/sse";

export default function ResearchPage() {
  const router = useRouter();
  const { events, answer, status, error, sessionId, score, start, cancel } = useResearchStream();

  useEffect(() => {
    if (status === "done" && sessionId) {
      router.prefetch(`/sessions/${sessionId}`);
    }
  }, [status, sessionId, router]);

  const streaming = status === "streaming";

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 px-6 py-8">
      <div>
        <h1 className="text-2xl font-semibold">Research</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">
          Four agents — Planner, Researcher, Synthesizer, Critic — collaborate to answer your query.
        </p>
      </div>

      <QueryComposer onSubmit={start} onCancel={cancel} streaming={streaming} />

      {error && (
        <div className="rounded-md border border-[var(--danger)]/40 bg-[var(--danger)]/10 px-3 py-2 text-sm text-[var(--danger)]">
          {error}
        </div>
      )}

      <AgentTrace events={events} />

      <AnswerPanel answer={answer} score={score} streaming={streaming && answer.length > 0} />

      {status === "done" && sessionId && (
        <a
          href={`/sessions/${sessionId}`}
          className="text-sm font-medium text-[var(--primary)] hover:underline"
        >
          View full session →
        </a>
      )}
    </div>
  );
}
