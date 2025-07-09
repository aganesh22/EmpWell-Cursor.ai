import { Route, Routes, Navigate } from "react-router-dom";
import Home from "./Home";
import React from "react";
import Login from "./Login";
import Register from "./Register";
import AdminDashboard from "./AdminDashboard";
import Who5Test from "./Who5Test";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/test/who5" element={<Who5Test />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}