import Link from "next/link";
import { Button } from "@/components/ui/Button";

const agents = [
  { name: "Planner", color: "var(--planner)", desc: "Breaks the query into a search strategy." },
  { name: "Researcher", color: "var(--researcher)", desc: "Calls tools — search, fetch, retrieve memory." },
  { name: "Synthesizer", color: "var(--synthesizer)", desc: "Composes a grounded, cited answer." },
  { name: "Critic", color: "var(--critic)", desc: "Scores the answer. Loops back if it's weak." },
];

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-1 flex-col">
      <header className="flex h-14 items-center justify-between px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <span className="inline-block h-6 w-6 rounded-md bg-[var(--primary)]" />
          AgentForge
        </Link>
        <nav className="flex items-center gap-2">
          <Link href="/login">
            <Button variant="ghost" size="sm">Sign in</Button>
          </Link>
          <Link href="/signup">
            <Button size="sm">Get started</Button>
          </Link>
        </nav>
      </header>

      <main className="flex flex-1 flex-col items-center px-6">
        <section className="flex max-w-3xl flex-col items-center pt-24 pb-16 text-center">
          <span className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1 text-xs text-[var(--muted)]">
            Multi-agent research, streamed in real time
          </span>
          <h1 className="mt-6 text-4xl font-semibold leading-tight sm:text-5xl">
            Ask a hard question.{" "}
            <span className="text-[var(--primary)]">Watch four agents</span> answer it.
          </h1>
          <p className="mt-5 max-w-xl text-base text-[var(--muted)]">
            AgentForge orchestrates a Planner, Researcher, Synthesizer, and Critic to deliver
            grounded answers — with full tool-call traces and quality scoring.
          </p>
          <div className="mt-8 flex gap-3">
            <Link href="/signup">
              <Button size="lg">Start researching</Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="secondary">
                Sign in
              </Button>
            </Link>
          </div>
        </section>

        <section className="grid w-full max-w-4xl grid-cols-1 gap-4 pb-24 sm:grid-cols-2">
          {agents.map((a) => (
            <div
              key={a.name}
              className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-5"
            >
              <div className="flex items-center gap-2">
                <span
                  className="inline-block h-2.5 w-2.5 rounded-full"
                  style={{ background: a.color }}
                />
                <h3 className="font-semibold">{a.name}</h3>
              </div>
              <p className="mt-2 text-sm text-[var(--muted)]">{a.desc}</p>
            </div>
          ))}
        </section>
      </main>

      <footer className="border-t border-[var(--border)] px-6 py-4 text-center text-xs text-[var(--muted)]">
        © {new Date().getFullYear()} AgentForge
      </footer>
    </div>
  );
}
