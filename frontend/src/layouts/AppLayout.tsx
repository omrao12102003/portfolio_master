import { Outlet, NavLink } from "react-router-dom"

const navigation: { label: string; path: string }[] = [
  { label: "Dashboard", path: "/" },
  { label: "Portfolio", path: "/portfolio" },
  { label: "Optimization", path: "/optimization" },
  { label: "Frontier", path: "/frontier" },
  { label: "Risk", path: "/risk" },
  { label: "Backtest", path: "/backtest" },
  { label: "Research", path: "/research" },
  { label: "RL", path: "/rl" },
]

export default function AppLayout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">P</div>
          <div>
            <strong>Portfolio Master</strong>
            <span>Quantitative Research</span>
          </div>
        </div>

        <nav>
          {navigation.map(({ label, path }) => (
            <NavLink
              key={path}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                isActive ? "nav-link active" : "nav-link"
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          MSc Quant Finance Platform
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">Investment Research Platform</span>
            <h1>Portfolio Master</h1>
          </div>
          <span className="environment">LOCAL</span>
        </header>

        <section className="page-content">
          <Outlet />
        </section>
      </main>
    </div>
  )
}
