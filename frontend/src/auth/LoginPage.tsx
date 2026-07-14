import { FormEvent, useState } from "react";
import { useDispatch } from "react-redux";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../services/api";
import { setTokens } from "./authSlice";

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@rpex.local");
  const [password, setPassword] = useState("admin12345");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      const response = await api.post("/auth/login", { email, password });
      const role = (response.data.role ?? "ADMIN") as "ADMIN";
      dispatch(
        setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token,
          role
        })
      );
      navigate("/");
    } catch {
      setError("Invalid credentials");
    }
  }

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <form className="card w-full max-w-md p-8" onSubmit={handleSubmit}>
        <h1 className="font-display text-3xl text-ink">RPEX CRM Login</h1>
        <p className="text-sm text-steel mt-2">Enterprise SEO inquiry operations cockpit.</p>

        <div className="mt-6 space-y-4">
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            type="email"
          />
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            type="password"
          />
        </div>

        {error ? <p className="text-red-600 text-sm mt-4">{error}</p> : null}

        <button className="btn-primary mt-6 w-full py-3">
          Login
        </button>

        <p className="text-sm text-steel mt-4 text-center">
          Need an account? <Link to="/register" className="text-ink font-semibold">Register User</Link>
        </p>
      </form>
    </div>
  );
}
