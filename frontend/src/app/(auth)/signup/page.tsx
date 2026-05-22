"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { api, ApiError } from "@/lib/api";
import { saveTokens } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    setLoading(true);
    try {
      const tokens = await api.auth.signup(email, password);
      saveTokens(tokens);
      router.push("/research");
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 409
          ? "An account with that email already exists"
          : "Signup failed",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">Create your account</h1>
        <p className="mt-1 text-sm text-[var(--muted)]">Start running multi-agent research in minutes.</p>
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
          minLength={8}
          autoComplete="new-password"
          hint="Minimum 8 characters"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <Input
          name="confirm"
          type="password"
          label="Confirm password"
          required
          autoComplete="new-password"
          value={confirm}
          onChange={(e) => setConfirm(e.target.value)}
        />
        {error && <p className="text-sm text-[var(--danger)]">{error}</p>}
        <Button type="submit" loading={loading}>
          Create account
        </Button>
      </form>
      <p className="text-center text-sm text-[var(--muted)]">
        Already have an account?{" "}
        <Link href="/login" className="font-medium text-[var(--primary)] hover:underline">
          Sign in
        </Link>
      </p>
    </div>
  );
}
