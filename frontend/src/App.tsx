import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { Dashboard } from "./pages/Dashboard";
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
            element={
              <PlaceholderPage
                title="Portfolio Optimization"
                description="Run classical optimization strategies and compare portfolio characteristics."
              />
            }
          />
          <Route
            path="/risk"
            element={
              <PlaceholderPage
                title="Risk Analytics"
                description="Analyze volatility, drawdown, VaR, expected shortfall and portfolio risk contribution."
              />
            }
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
