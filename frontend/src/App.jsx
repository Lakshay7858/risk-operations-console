import React from "react";
import { BrowserRouter as Router, Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard";

const navStyle = {
  display: "flex",
  alignItems: "center",
  gap: "24px",
  padding: "0 32px",
  height: "56px",
  background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
  color: "#e0e0e0",
  fontFamily: "'Segoe UI', Roboto, sans-serif",
  fontSize: "14px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
};

const logoStyle = {
  fontSize: "18px",
  fontWeight: 700,
  color: "#00d4ff",
  marginRight: "auto",
  letterSpacing: "0.5px",
};

const linkStyle = {
  color: "#a0aec0",
  textDecoration: "none",
  padding: "6px 12px",
  borderRadius: "4px",
  transition: "all 0.2s ease",
};

const activeLinkStyle = {
  ...linkStyle,
  color: "#00d4ff",
  backgroundColor: "rgba(0,212,255,0.1)",
};

function App() {
  return (
    <Router>
      <div style={{ minHeight: "100vh", backgroundColor: "#0f0f23" }}>
        <nav style={navStyle}>
          <span style={logoStyle}>Trade Analytics</span>
          <NavLink
            to="/"
            end
            style={({ isActive }) => (isActive ? activeLinkStyle : linkStyle)}
          >
            Dashboard
          </NavLink>
          <NavLink
            to="/trades"
            style={({ isActive }) => (isActive ? activeLinkStyle : linkStyle)}
          >
            Declarations
          </NavLink>
          <NavLink
            to="/risk"
            style={({ isActive }) => (isActive ? activeLinkStyle : linkStyle)}
          >
            Risk Analysis
          </NavLink>
        </nav>

        <main style={{ padding: "24px 32px" }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route
              path="/trades"
              element={
                <div style={{ color: "#e0e0e0" }}>
                  <h2>Trade Declarations</h2>
                  <p>Searchable, filterable list of customs declarations.</p>
                </div>
              }
            />
            <Route
              path="/risk"
              element={
                <div style={{ color: "#e0e0e0" }}>
                  <h2>Risk Analysis</h2>
                  <p>Detailed risk scoring and distribution views.</p>
                </div>
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
