import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { Dashboard } from "./pages/Dashboard";
import { OptimizationPanel } from "./components/OptimizationPanel";
import { RiskDashboard } from "./components/RiskDashboard";
import { FrontierDashboard } from "./components/FrontierDashboard";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import "./styles.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route
            path="/portfolio"
            element={
              <PlaceholderPage
                title="Portfolio Builder"
                description="Construct portfolios, define constraints and inspect target allocations."
              />
            }
          />
          <Route
            path="/optimization"
            element={<OptimizationPanel />}
          />
          <Route
            path="/risk"
            element={<RiskDashboard />}
          />
          <Route
            path="/frontier"
            element={<FrontierDashboard />}
          />
          <Route
            path="/backtesting"
            element={
              <PlaceholderPage
                title="Backtesting"
                description="Evaluate historical portfolio strategies with rebalancing and transaction costs."
              />
            }
          />
          <Route
            path="/research"
            element={
              <PlaceholderPage
                title="Investment Research"
                description="Research documents, quantitative signals and AI-assisted financial analysis."
              />
            }
          />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
