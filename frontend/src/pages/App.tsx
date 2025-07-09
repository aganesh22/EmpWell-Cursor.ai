import { Route, Routes, Navigate } from "react-router-dom";
import Home from "./Home";
import React from "react";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}