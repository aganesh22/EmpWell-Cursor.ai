import React from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { listResources, Resource } from "../lib/api";

export default function ResourcesPage() {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();
  if (!token) navigate("/login");

  const { data, isPending, isError } = useQuery({
    queryKey: ["resources"],
    queryFn: () => listResources(token!),
  });

  if (isPending) return <p>Loading…</p>;
  if (isError) return <p>Error loading resources.</p>;

  const resources: Resource[] = data!.data;

  return (
    <main style={{ padding: 24 }}>
      <h2>Resources & Recommendations</h2>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill,minmax(250px,1fr))", gap: 16 }}>
        {resources.map((r) => (
          <div key={r.id} style={{ border: "1px solid #e5e7eb", padding: 12, borderRadius: 8 }}>
            <h4>{r.title}</h4>
            <p>{r.description}</p>
            <a href={r.url} target="_blank" rel="noreferrer">
              View {r.type}
            </a>
          </div>
        ))}
      </div>
    </main>
  );
}