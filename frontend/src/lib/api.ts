/// <reference types="vite/client" />
import axios from "axios";
import { getAllTests, getTestByKey } from './test-library';

// Use mock API in development environments without backend
const API_BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const IS_MOCK_ENV = API_BASE_URL.includes("mock") || !import.meta.env.VITE_API_URL;

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Mock data for development
const MOCK_USER = {
  id: 1,
  email: "demo@example.com",
  full_name: "Demo User",
  department: "Engineering",
  is_active: true,
  role: "employee"
};

const MOCK_TOKEN = "mock-jwt-token-for-demo";

const MOCK_RESOURCES = [
  {
    id: 1,
    title: "Mindfulness Basics",
    description: "Short article on starting mindfulness.",
    url: "https://example.com/mindfulness",
    type: "article",
    tags: "wellbeing,stress"
  },
  {
    id: 2,
    title: "Breathing Techniques",
    description: "Guided breathing exercise video.",
    url: "https://example.com/breathing",
    type: "video",
    tags: "stress"
  }
];

// Mock API interceptor
if (IS_MOCK_ENV) {
  api.interceptors.request.use((config) => {
    console.log(`[MOCK API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  });

  api.interceptors.response.use(
    (response) => response,
    (error) => {
      // Return mock responses for demo
      const url = error.config?.url || "";
      
      if (url.includes("/auth/register")) {
        return Promise.resolve({ data: MOCK_USER, status: 201 });
      }
      if (url.includes("/auth/login")) {
        return Promise.resolve({ data: { access_token: MOCK_TOKEN, token_type: "bearer" }, status: 200 });
      }
      if (url.includes("/auth/me")) {
        return Promise.resolve({ data: MOCK_USER, status: 200 });
      }
      if (url.includes("/resources")) {
        return Promise.resolve({ data: MOCK_RESOURCES, status: 200 });
      }
      if (url.includes("/tests/")) {
        const pathParts = url.split("/tests/");
        if (pathParts[1] && pathParts[1] !== '') {
          // Get specific test
          const testKey = pathParts[1];
          const mockTest = getTestByKey(testKey);
          if (mockTest) {
            return Promise.resolve({ data: mockTest, status: 200 });
          }
        } else {
          // List all tests
          const allTests = getAllTests();
          return Promise.resolve({ data: allTests, status: 200 });
        }
        
        // Fallback for unknown tests
        const mockTest = {
          key: "who5",
          name: "WHO-5 Wellbeing Index",
          description: "Measure current mental wellbeing",
          category: "wellbeing",
          duration_minutes: 2,
          branching_enabled: false,
          questions: [
            { id: 1, text: "I have felt cheerful and in good spirits", order: 1, min_value: 0, max_value: 5, weight: 1.0, question_type: "likert", required: true, reverse_scored: false }
          ],
          scoring_rules: { type: "simple_sum" },
          interpretation_guide: { score_ranges: [], recommendations: [], risk_indicators: [] }
        };
        return Promise.resolve({ data: mockTest, status: 200 });
      }
      
      return Promise.reject(error);
    }
  );
}

export interface RegisterPayload {
  email: string;
  full_name?: string;
  password: string;
  department?: string;
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

export interface User {
  id: number;
  email: string;
  full_name?: string;
  department?: string;
  is_active: boolean;
  role: string;
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

export function getMe(token: string) {
  return api.get<User>("/auth/me", { headers: { Authorization: `Bearer ${token}` } });
}

export interface Question {
  id: number;
  text: string;
  order: number;
  min_value: number;
  max_value: number;
}

export interface TestTemplate {
  key: string;
  name: string;
  description?: string;
  questions: Question[];
}

export function listTests(token: string) {
  return api.get<TestTemplate[]>("/tests", { headers: { Authorization: `Bearer ${token}` } });
}

export function getTest(token: string, key: string) {
  return api.get<TestTemplate>(`/tests/${key}`, { headers: { Authorization: `Bearer ${token}` } });
}

export interface TestResult {
  raw_score: number;
  normalized_score: number;
  interpretation: string;
  tips: string[];
}

export function submitTest(token: string, key: string, answers: number[]) {
  return api.post<TestResult>(`/tests/${key}/submit`, answers, { headers: { Authorization: `Bearer ${token}` } });
}

export function fetchAggregate(token: string, byDept = true, days = 180) {
  return api.get<any>(`/reports/aggregate?by_department=${byDept}&days=${days}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export interface Resource {
  id: number;
  title: string;
  description?: string;
  url: string;
  type: string;
  tags?: string;
}

export function listResources(token: string) {
  return api.get<Resource[]>("/resources", { headers: { Authorization: `Bearer ${token}` } });
}