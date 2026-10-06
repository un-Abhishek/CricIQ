import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import { Activity, BarChart3, MapPin, Shield, Swords, Target, Users, Trophy } from "lucide-react";
import "./App.css";
import Dashboard from "./pages/Dashboard";
import Batting from "./pages/Batting";
import { Bowling, Teams, HeadToHead, Venues, Players } from "./pages/AnalyticsPages";

const navigation = [
  ["/", "Dashboard", Activity],
  ["/batting", "Batting", Target],
  ["/bowling", "Bowling", BarChart3],
  ["/teams", "Teams", Shield],
  ["/head-to-head", "Head-to-Head", Swords],
  ["/venues", "Venues", MapPin],
  ["/players", "Players", Users]
];

export function AppShell({ children }) {
  return (
    <div className="site-shell">
      <header className="topbar">
        <NavLink to="/" className="brand">
          <span className="brand-ball">◒</span>
          <span>
            CRIC<span>IQ</span>
          </span>
        </NavLink>
        <nav aria-label="Main navigation">
          {navigation.map(([to, label, Icon]) => (
            <NavLink
              end={to === "/"}
              to={to}
              key={to}
              className={({ isActive }) => (isActive ? "active" : "")}
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
        <span className="data-status">
          <i /> Live IPL Analytics
        </span>
      </header>

      {children}

      <footer
        style={{
          borderTop: "1px solid var(--line)",
          padding: "30px 0",
          background: "rgba(6, 13, 9, 0.95)",
          color: "var(--muted)",
          fontSize: "13px",
          textAlign: "center",
          marginTop: "40px"
        }}
      >
        <div style={{ width: "min(1240px, calc(100% - 40px))", margin: "0 auto", display: "flex", justifyContent: "center", flexWrap: "wrap", gap: 16, alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ color: "var(--accent)", fontWeight: "bold" }}>CRICIQ ANALYTICS</span>
            <span>· Ball-By-Ball Insights Engine</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

function Routed({ children }) {
  return <AppShell>{children}</AppShell>;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Routed><Dashboard /></Routed>} />
        <Route path="/batting" element={<Routed><Batting /></Routed>} />
        <Route path="/bowling" element={<Routed><Bowling /></Routed>} />
        <Route path="/teams" element={<Routed><Teams /></Routed>} />
        <Route path="/head-to-head" element={<Routed><HeadToHead /></Routed>} />
        <Route path="/venues" element={<Routed><Venues /></Routed>} />
        <Route path="/players" element={<Routed><Players /></Routed>} />
      </Routes>
    </BrowserRouter>
  );
}
