"use client";

import { useState, type FormEvent, type KeyboardEvent } from "react";
import { Button } from "@/components/ui/Button";

interface QueryComposerProps {
  onSubmit: (query: string) => void;
  onCancel?: () => void;
  streaming: boolean;
}

export function QueryComposer({ onSubmit, onCancel, streaming }: QueryComposerProps) {
  const [query, setQuery] = useState("");

  function submit() {
    const trimmed = query.trim();
    if (!trimmed || streaming) return;
    onSubmit(trimmed);
    setQuery("");
  }

  function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    submit();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3 shadow-sm"
    >
      <textarea
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onKeyDown={handleKeyDown}
        rows={3}
        placeholder="Ask anything. Try: Compare LangGraph vs CrewAI for production multi-agent systems."
        className="w-full resize-none bg-transparent text-sm text-[var(--foreground)] placeholder:text-[var(--muted)] focus:outline-none"
        disabled={streaming}
      />
      <div className="flex items-center justify-between pt-2">
        <span className="text-xs text-[var(--muted)]">⌘/Ctrl + Enter to submit</span>
        {streaming && onCancel ? (
          <Button type="button" variant="secondary" size="sm" onClick={onCancel}>
            Stop
          </Button>
        ) : (
          <Button type="submit" size="sm" disabled={!query.trim()}>
            Research
          </Button>
        )}
      </div>
    </form>
  );
}
