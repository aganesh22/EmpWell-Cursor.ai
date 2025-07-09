/// <reference types="vite/client" />
import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:8000",
});

export interface RegisterPayload {
  email: string;
  full_name?: string;
  password: string;
}

export function registerUser(data: RegisterPayload) {
  return api.post("/auth/register", data);
}

export interface LoginPayload {
  email: string;
  password: string;
}

export function loginUser({ email, password }: LoginPayload) {
  const form = new URLSearchParams();
  form.append("username", email);
  form.append("password", password);
  return api.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
}

export function loginWithGoogle(id_token: string) {
  return api.post("/auth/google", { id_token });
}