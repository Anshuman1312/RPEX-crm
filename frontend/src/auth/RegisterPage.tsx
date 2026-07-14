import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../services/api";

export default function RegisterPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [roleName, setRoleName] = useState("ADMIN");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    try {
      await api.post("/auth/register", {
        name,
        email,
        password,
        role_name: roleName
      });
      setSuccess("Registration successful. You can login now.");
      setTimeout(() => navigate("/login"), 700);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Registration failed");
    }
  }

  return (
    <div className="min-h-screen grid place-items-center p-6">
      <form className="card w-full max-w-lg p-8" onSubmit={handleSubmit}>
        <h1 className="font-display text-3xl text-ink">Create User</h1>
        <p className="text-sm text-steel mt-2">Create CRM users with role assignment.</p>

        <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Full Name"
            required
          />
          <select className="w-full rounded-xl border border-slate-200 px-4 py-3" value={roleName} onChange={(e) => setRoleName(e.target.value)}>
            <option value="ADMIN">ADMIN</option>
            <option value="SEO_MANAGER">SEO_MANAGER</option>
            <option value="SALES">SALES</option>
            <option value="ANALYST">ANALYST</option>
          </select>
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3 md:col-span-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            type="email"
            required
          />
          <input
            className="w-full rounded-xl border border-slate-200 px-4 py-3 md:col-span-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            type="password"
            required
          />
        </div>

        {error ? <p className="text-red-600 text-sm mt-4">{error}</p> : null}
        {success ? <p className="text-green-700 text-sm mt-4">{success}</p> : null}

        <button className="btn-primary mt-6 w-full py-3">Register</button>

        <p className="text-sm text-steel mt-4 text-center">
          Already have an account? <Link to="/login" className="text-ink font-semibold">Login</Link>
        </p>
      </form>
    </div>
  );
}
