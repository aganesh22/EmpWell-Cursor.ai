import React from "react";
import { Link } from "react-router-dom";

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
        <p>
          You are logged in. <Link to="/test/who5">Take WHO-5 Test</Link> | <Link to="/admin">Admin Dashboard</Link>
        </p>
      ) : (
        <p>
          <Link to="/login">Login</Link> or <Link to="/register">Register</Link>
        </p>
      )}
    </main>
  );
}