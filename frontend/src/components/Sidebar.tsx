import { NavLink } from "react-router-dom";
import { ConnectionStatus } from "./ConnectionStatus";
import { useEffect, useState } from "react";
import { api } from "../services/api";

const navigation = [
  { label: "Dashboard", path: "/" },
  { label: "Portfolio", path: "/portfolio" },
  { label: "Optimization", path: "/optimization" },
  { label: "Risk", path: "/risk" },
  { label: "Backtesting", path: "/backtesting" },
  { label: "Research", path: "/research" },
];

export function Sidebar() {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.health()
      .then(() => setConnected(true))
      .catch(() => setConnected(false))
      .finally(() => setLoading(false));
  }, []);
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">P</div>
        <div>
          <div className="brand-name">Portfolio AI</div>
          <div className="brand-subtitle">Quant Research Platform</div>
        </div>
      </div>

      <nav className="navigation">
        {navigation.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `nav-item ${isActive ? "active" : ""}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <ConnectionStatus connected={connected} loading={loading} />
    </aside>
  );
}
