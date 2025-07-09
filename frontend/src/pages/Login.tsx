/// <reference types="vite/client" />
import React, { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useMutation } from "@tanstack/react-query";
import { loginUser, loginWithGoogle } from "../lib/api";
import { GoogleAuth } from "../lib/google-auth";

export default function Login() {
  const navigate = useNavigate();
  const googleButtonRef = useRef<HTMLDivElement>(null);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const mutation = useMutation({
    mutationFn: loginUser,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      navigate("/");
    },
  });

  const googleMutation = useMutation({
    mutationFn: loginWithGoogle,
    onSuccess: (data) => {
      localStorage.setItem("token", data.data.access_token);
      setIsGoogleLoading(false);
      navigate("/");
    },
    onError: () => {
      setIsGoogleLoading(false);
    },
  });

  // Enhanced Google SSO setup
  useEffect(() => {
    const setupGoogleAuth = async () => {
      const googleAuth = GoogleAuth.getInstance();
      
      if (!googleAuth.isConfigured()) {
        console.log("Google SSO not configured - skipping");
        return;
      }

      try {
        await googleAuth.initialize();
        
        // Render the Google Sign-In button
        if (googleButtonRef.current) {
          googleAuth.renderSignInButton(googleButtonRef.current, {
            theme: 'outline',
            size: 'large',
            text: 'signin_with',
            shape: 'rectangular',
          });
        }

        // Listen for Google sign-in events
        const handleGoogleSignIn = (event: CustomEvent) => {
          setIsGoogleLoading(true);
          googleMutation.mutate(event.detail.credential);
        };

        window.addEventListener('google-signin', handleGoogleSignIn as EventListener);
        
        return () => {
          window.removeEventListener('google-signin', handleGoogleSignIn as EventListener);
        };
      } catch (error) {
        console.error("Failed to initialize Google Auth:", error);
      }
    };

    setupGoogleAuth();
  }, [googleMutation]);

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
      {googleMutation.isError && <p style={{ color: "red" }}>Google sign-in failed</p>}
      
      <div style={{ marginTop: 20, textAlign: 'center' }}>
        <div style={{ margin: '16px 0', fontSize: '14px', color: '#666' }}>or</div>
        <div ref={googleButtonRef} style={{ display: 'flex', justifyContent: 'center' }}>
          {isGoogleLoading && <p>Signing in with Google...</p>}
        </div>
      </div>
      
      <p style={{ marginTop: 16 }}>
        Don't have an account? <Link to="/register">Register</Link>
      </p>
    </main>
  );
}