import React from "react";
import { Link } from "react-router-dom";
import NotificationSystem from "../components/NotificationSystem";

export default function Home() {
  const token = localStorage.getItem("token");

  return (
    <main
      style={{
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <h1>Corporate Wellbeing Platform</h1>
      {token ? (
        <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: '20px' }}>
          <p>
            You are logged in. <Link to="/resources">Resources</Link> | <Link to="/test/who5">WHO-5</Link> | <Link to="/test/mbti">MBTI</Link> | <Link to="/test/disc">DISC</Link> | <Link to="/admin">Admin</Link> | <Link to="/admin/dashboard">Analytics Dashboard</Link>
          </p>
          <NotificationSystem userId={1} isAdmin={true} />
        </div>
      ) : (
        <p>
          <Link to="/login">Login</Link> or <Link to="/register">Register</Link>
        </p>
      )}
    </main>
  );
}