import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchAggregate } from "../lib/api";
import { Line, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { useNavigate } from "react-router-dom";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title, Tooltip, Legend);

export default function AdminAnalytics() {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();
  if (!token) {
    navigate("/login");
  }

  const { data, isPending, isError } = useQuery({
    queryKey: ["aggregate"],
    queryFn: () => fetchAggregate(token!),
  });

  if (isPending) return <p>Loading…</p>;
  if (isError) return <p>Error loading analytics.</p>;

  const agg = data!.data;

  // WHO-5 trend
  const trendLabels = agg.who5?.trend.map((t: [string, number]) => t[0]) || [];
  const trendValues = agg.who5?.trend.map((t: [string, number]) => t[1]) || [];

  const mbtiCounts = agg.mbti?.counts || {};
  const mbtiLabels = Object.keys(mbtiCounts);
  const mbtiValues = Object.values(mbtiCounts);

  const discCounts = agg.disc?.counts || {};
  const discLabels = Object.keys(discCounts);
  const discValues = Object.values(discCounts);

  return (
    <main style={{ padding: 24 }}>
      <h2>Organisation Analytics</h2>

      <section style={{ marginTop: 32 }}>
        <h3>WHO-5 Wellbeing Trend (last 6 months)</h3>
        <Line
          data={{
            labels: trendLabels,
            datasets: [
              {
                label: "Average Score",
                data: trendValues,
                borderColor: "#3b82f6",
                backgroundColor: "rgba(59,130,246,0.3)",
              },
            ],
          }}
        />
      </section>

      <section style={{ marginTop: 32 }}>
        <h3>MBTI Type Distribution</h3>
        <Bar
          data={{
            labels: mbtiLabels,
            datasets: [
              {
                label: "Count",
                data: mbtiValues,
                backgroundColor: "#10b981",
              },
            ],
          }}
        />
      </section>

      <section style={{ marginTop: 32 }}>
        <h3>DISC Style Distribution</h3>
        <Bar
          data={{
            labels: discLabels,
            datasets: [
              {
                label: "Count",
                data: discValues,
                backgroundColor: "#f59e0b",
              },
            ],
          }}
        />
      </section>
    </main>
  );
}