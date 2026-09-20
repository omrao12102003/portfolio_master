import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import Dashboard from "./pages/Dashboard";
import { OptimizationPanel } from "./components/OptimizationPanel";
import { FrontierDashboard } from "./components/FrontierDashboard";
import { RiskDashboard } from "./components/RiskDashboard";
import { BacktestDashboard } from "./components/BacktestDashboard";
import RLDashboard from "./components/RLDashboard";
import ResearchPage from "./pages/ResearchPage";
import PortfolioPage from "./pages/PortfolioPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/portfolio" element={<PortfolioPage />} />
        <Route path="/optimization" element={<OptimizationPanel />} />
        <Route path="/frontier" element={<FrontierDashboard />} />
        <Route path="/risk" element={<RiskDashboard />} />
        <Route path="/backtesting" element={<BacktestDashboard />} />
        <Route path="/backtest" element={<BacktestDashboard />} />
        <Route path="/rl" element={<RLDashboard />} />
        <Route path="/research" element={<ResearchPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
