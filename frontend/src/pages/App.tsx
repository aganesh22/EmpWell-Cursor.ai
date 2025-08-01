import { Route, Routes, Navigate } from "react-router-dom";
import Home from "./Home";
import React from "react";
import Login from "./Login";
import Register from "./Register";
import AdminDashboard from "./AdminDashboard";
import EnhancedAdminDashboard from "./EnhancedAdminDashboard";
import Who5Test from "./Who5Test";
import MBTITest from "./MBTITest";
import DISCTest from "./DISCTest";
import AdminAnalytics from "./AdminAnalytics";
import ResourcesPage from "./Resources";
import TestLibrary from "./TestLibrary";
import TestTaker from "./TestTaker";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/analytics" element={<AdminAnalytics />} />
      <Route path="/admin/dashboard" element={<EnhancedAdminDashboard />} />
      <Route path="/tests" element={<TestLibrary />} />
      <Route path="/test/:testKey" element={<TestTaker />} />
      {/* Legacy test routes for backward compatibility */}
      <Route path="/test/who5" element={<Who5Test />} />
      <Route path="/test/mbti" element={<MBTITest />} />
      <Route path="/test/disc" element={<DISCTest />} />
      <Route path="/resources" element={<ResourcesPage />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}