import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./styles/globals.css";

import App from "./pages/App";
// Global theme styles
import "./styles/theme.css";

import { ThemeProvider } from "./lib/theme";
import ThemeToggle from "./components/ThemeToggle";

const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <App />
          {/* Floating theme switcher visible on all pages */}
          <ThemeToggle />
        </BrowserRouter>
      </QueryClientProvider>
    </ThemeProvider>
  </React.StrictMode>
);