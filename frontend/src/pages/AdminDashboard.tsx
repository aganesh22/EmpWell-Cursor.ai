import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  listUsers,
  inviteUserApi,
  updateUserStatusApi,
  resetPasswordApi,
  User,
  getMe,
} from "../lib/api";
import { useNavigate } from "react-router-dom";

export default function AdminDashboard() {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  if (!token) {
    navigate("/");
  }

  // Fetch current user to ensure admin role
  const meQuery = useQuery({
    queryKey: ["me"],
    queryFn: () => getMe(token!),
  });

  const usersQuery = useQuery({
    queryKey: ["users"],
    queryFn: () => listUsers(token!),
    enabled: !!token,
  });

  const inviteMutation = useMutation({
    mutationFn: (data: { email: string; full_name?: string; role: string }) => inviteUserApi(token!, data),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const statusMutation = useMutation({
    mutationFn: ({ userId, is_active }: { userId: number; is_active: boolean }) =>
      updateUserStatusApi(token!, userId, is_active),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const resetMutation = useMutation({
    mutationFn: ({ userId, password }: { userId: number; password: string }) =>
      resetPasswordApi(token!, userId, password),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["users"] }),
  });

  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteName, setInviteName] = useState("");

  function handleInvite(e: React.FormEvent) {
    e.preventDefault();
    inviteMutation.mutate({ email: inviteEmail, full_name: inviteName, role: "employee" });
  }

  if (meQuery.isLoading) return <p>Loading…</p>;

  if (meQuery.isError || meQuery.data?.data.role !== "admin") {
    return (
      <main style={{ padding: 24 }}>
        <p>Access denied. Admins only.</p>
      </main>
    );
  }

  return (
    <main style={{ padding: 24 }}>
      <h2>Admin Dashboard – Users</h2>

      <section style={{ marginTop: 24 }}>
        <h3>Invite User</h3>
        <form onSubmit={handleInvite} style={{ display: "flex", gap: 8 }}>
          <input
            type="email"
            placeholder="Email"
            value={inviteEmail}
            onChange={(e) => setInviteEmail(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="Full Name (optional)"
            value={inviteName}
            onChange={(e) => setInviteName(e.target.value)}
          />
          <button type="submit" disabled={inviteMutation.isPending}>
            Invite
          </button>
        </form>
      </section>

      <section style={{ marginTop: 32 }}>
        <h3>All Users</h3>
        {usersQuery.isPending ? (
          <p>Loading…</p>
        ) : usersQuery.isError ? (
          <p>Error loading users</p>
        ) : (
          <table border={1} cellPadding={6} style={{ borderCollapse: "collapse", width: "100%" }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Email</th>
                <th>Name</th>
                <th>Role</th>
                <th>Active</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {usersQuery.data?.data.map((u: User) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td>{u.email}</td>
                  <td>{u.full_name}</td>
                  <td>{u.role}</td>
                  <td>{u.is_active ? "✅" : "❌"}</td>
                  <td>
                    <button
                      onClick={() => statusMutation.mutate({ userId: u.id, is_active: !u.is_active })}
                      disabled={statusMutation.isPending}
                    >
                      {u.is_active ? "Disable" : "Enable"}
                    </button>{" "}
                    <button
                      onClick={() => {
                        const pwd = prompt("New password for user? (will override)");
                        if (pwd) {
                          resetMutation.mutate({ userId: u.id, password: pwd });
                        }
                      }}
                    >
                      Reset Password
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}