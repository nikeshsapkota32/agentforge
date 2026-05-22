"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api, ApiError } from "@/lib/api";
import { saveTokens } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const tokens = await api.auth.login(email, password);
      saveTokens(tokens);
      router.push("/research");
    } catch (err) {
      setError(err instanceof ApiError && err.status === 401 ? "Invalid email or password" : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Welcome back</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Sign in to continue your research.</p>
      </div>
      <form onSubmit={onSubmit} className="flex flex-col gap-4">
        <Input
          name="email"
          type="email"
          label="Email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <Input
          name="password"
          type="password"
          label="Password"
          required
          autoComplete="current-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
        <Button type="submit" loading={loading}>
          Sign in
        </Button>
      </form>
      <p className="text-center text-sm text-[var(--muted)]">
        New to AgentForge?{" "}
        <Link href="/signup" className="font-medium text-[var(--primary)] hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}
