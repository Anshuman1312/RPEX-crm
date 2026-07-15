import { FormEvent, useState } from "react";
import { useDispatch } from "react-redux";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../services/api";
import { RoleName, setTokens } from "./authSlice";

type LoginPageProps = {
  partnerMode?: boolean;
};

export default function LoginPage({ partnerMode = false }: LoginPageProps) {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    try {
      const response = await api.post("/auth/login", { email, password });
      const role = (response.data.role ?? "ADMIN") as RoleName;

      if (partnerMode && role !== "CHANNEL_PARTNER") {
        setError("This login is only for channel partner accounts.");
        return;
      }

      dispatch(
        setTokens({
          accessToken: response.data.access_token,
          refreshToken: response.data.refresh_token,
          role
        })
      );

      navigate(partnerMode ? "/partner" : "/");
    } catch {
      setError("Invalid credentials");
    }
  }

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <form className="card w-full max-w-md p-8" onSubmit={handleSubmit}>
        <h1 className="font-display text-3xl text-ink">{partnerMode ? "Channel Partner Login" : "RPEX CRM Login"}</h1>
        <p className="text-sm text-steel mt-2">
          {partnerMode ? "Access your own bookings, collections, documents, and partner segments." : "Enterprise SEO inquiry operations cockpit."}
        </p>

        <div className="mt-6 space-y-4">
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="admin@rpex.local"
            type="email"
          />

          <div className="relative">
            <input
              className="w-full rounded-xl border border-slate-200 px-4 py-3 pr-20"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="admin12345"
              type={showPassword ? "text" : "password"}
            />
            <button
              type="button"
              className="absolute right-2 top-1/2 -translate-y-1/2 rounded-lg px-3 py-1 text-xs font-semibold text-slate-300 hover:bg-slate-800"
              onClick={() => setShowPassword((current) => !current)}
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
        </div>

        {error ? <p className="text-red-600 text-sm mt-4">{error}</p> : null}

        <button className="btn-primary mt-6 w-full py-3">Login</button>

        <p className="text-sm text-steel mt-4 text-center">
          {partnerMode ? (
            <>
              Internal user? <Link to="/login" className="text-ink font-semibold">Back to CRM Login</Link>
            </>
          ) : (
            <>
              Need an account? <Link to="/register" className="text-ink font-semibold">Register User</Link>
            </>
          )}
        </p>

        {!partnerMode ? (
          <p className="text-sm text-steel mt-2 text-center">
            Channel partner? <Link to="/partner/login" className="text-cyan-300 font-semibold">Partner Login</Link>
          </p>
        ) : (
          <p className="text-sm text-steel mt-2 text-center">Use your partner credentials only.</p>
        )}
      </form>
    </div>
  );
}
