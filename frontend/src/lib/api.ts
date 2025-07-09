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

export function listUsers(token: string) {
  return api.get<User[]>("/users", { headers: { Authorization: `Bearer ${token}` } });
}

export function inviteUserApi(token: string, data: { email: string; full_name?: string; role: string }) {
  return api.post("/users/invite", data, { headers: { Authorization: `Bearer ${token}` } });
}

export function updateUserStatusApi(token: string, userId: number, is_active: boolean) {
  return api.patch(`/users/${userId}/status`, { is_active }, { headers: { Authorization: `Bearer ${token}` } });
}

export function resetPasswordApi(token: string, userId: number, password: string) {
  return api.post(`/users/${userId}/reset_password`, { password }, { headers: { Authorization: `Bearer ${token}` } });
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  role: string;
}

export function getMe(token: string) {
  return api.get<User>("/auth/me", { headers: { Authorization: `Bearer ${token}` } });
}