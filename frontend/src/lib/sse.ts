"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { env } from "./env";
import { getAccessToken } from "./auth";
import type { SSEEvent } from "./types";

export interface ResearchStreamState {
  events: SSEEvent[];
  answer: string;
  status: "idle" | "streaming" | "done" | "error";
  error?: string;
  sessionId?: string;
  score?: number;
}

const INITIAL: ResearchStreamState = {
  events: [],
  answer: "",
  status: "idle",
};

export function useResearchStream() {
  const [state, setState] = useState<ResearchStreamState>(INITIAL);
  const controllerRef = useRef<AbortController | null>(null);

  const start = useCallback(async (query: string, sessionId?: string) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setState({ ...INITIAL, status: "streaming" });

    try {
      const token = getAccessToken();
      const res = await fetch(`${env.apiUrl}/api/v1/research`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ query, session_id: sessionId }),
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        setState((s) => ({ ...s, status: "error", error: `HTTP ${res.status}` }));
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const frames = buffer.split("\n\n");
        buffer = frames.pop() ?? "";

        for (const frame of frames) {
          const line = frame.split("\n").find((l) => l.startsWith("data: "));
          if (!line) continue;
          const json = line.slice(6);
          try {
            const evt = JSON.parse(json) as SSEEvent;
            applyEvent(setState, evt);
          } catch {
            // ignore malformed frame
          }
        }
      }

      setState((s) => (s.status === "streaming" ? { ...s, status: "done" } : s));
    } catch (err) {
      if ((err as Error).name === "AbortError") return;
      setState((s) => ({ ...s, status: "error", error: (err as Error).message }));
    }
  }, []);

  const cancel = useCallback(() => {
    controllerRef.current?.abort();
    setState((s) => ({ ...s, status: "idle" }));
  }, []);

  const reset = useCallback(() => {
    controllerRef.current?.abort();
    setState(INITIAL);
  }, []);

  useEffect(() => () => controllerRef.current?.abort(), []);

  return { ...state, start, cancel, reset };
}

function applyEvent(
  setState: React.Dispatch<React.SetStateAction<ResearchStreamState>>,
  evt: SSEEvent,
) {
  setState((s) => {
    switch (evt.type) {
      case "token":
        return { ...s, events: [...s.events, evt], answer: s.answer + evt.text };
      case "done":
        return {
          ...s,
          events: [...s.events, evt],
          status: "done",
          sessionId: evt.sessionId,
          score: evt.score,
          answer: evt.answer || s.answer,
        };
      case "error":
        return { ...s, events: [...s.events, evt], status: "error", error: evt.message };
      default:
        return { ...s, events: [...s.events, evt] };
    }
  });
}
