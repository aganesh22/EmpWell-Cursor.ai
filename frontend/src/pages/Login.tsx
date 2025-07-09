/// <reference types="vite/client" />
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { loginUser, loginWithGoogle } from "../lib/api";

export default function Login() {
  const navigate = useNavigate();
  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      navigate("/");
    },
  });

  // Google One Tap
  React.useEffect(() => {
    /* global google */
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
    if (!clientId || !(window as any).google?.accounts) return;

    (window as any).google.accounts.id.initialize({
      client_id: clientId,
      callback: (response: any) => {
        googleMutation.mutate(response.credential);
      },
    });

    (window as any).google.accounts.id.renderButton(
      document.getElementById("google-btn"),
      { theme: "outline", size: "large" }
    );
  }, []);

  const googleMutation = useMutation({
    mutationFn: loginWithGoogle,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      navigate("/");
    },
  });

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    mutation.mutate({ email, password });
  }

  return (
    <main style={{ maxWidth: 400, margin: "2rem auto" }}>
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Email</label>
          <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div style={{ marginTop: 12 }}>
          <label>Password</label>
          <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button type="submit" disabled={mutation.isPending} style={{ marginTop: 16 }}>
          {mutation.isPending ? "Logging in..." : "Login"}
        </button>
      </form>
      {mutation.isError && <p style={{ color: "red" }}>Invalid credentials</p>}
      <div id="google-btn" style={{ marginTop: 16 }}></div>
      <p style={{ marginTop: 16 }}>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </main>
  );
}