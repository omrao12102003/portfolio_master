# Portfolio Master

## Quantitative Portfolio Analytics, Reinforcement Learning & AI Investment Research Platform

**Developed by:** Om Barot
**B.Tech Computer Science & Engineering — VIT Vellore, 2026**
**MSc International Accounting & Finance — Bayes Business School, City St George's, University of London, 2026–27**

Portfolio Master is an end-to-end quantitative finance and investment research platform developed as a technical and academic portfolio project. The system combines classical portfolio theory, risk management, historical backtesting, time-series and factor modelling, derivatives, fixed income, systematic trading research, reinforcement learning, and evidence-grounded financial document retrieval.

The project was designed around a simple principle:

> **Quantitative calculations should remain deterministic and auditable; AI should assist with research and explanation rather than become the source of financial truth.**

The platform is implemented as a Python/FastAPI backend with a React/TypeScript frontend and PostgreSQL/pgvector research storage. It is deployed without Docker using Render for the backend/database and Vercel for the frontend.

---

## 1. Project Objectives

Portfolio Master was developed to bring together the major components that appear in a modern quantitative investment workflow:

- Financial data ingestion and validation
- Return and portfolio analytics
- Classical portfolio optimization
- Efficient-frontier analysis
- Risk measurement and attribution
- Historical portfolio backtesting
- Time-series forecasting
- CAPM and Fama-French factor analysis
- Advanced risk and scenario analysis
- Derivative pricing and Greeks
- Fixed-income analytics
- Trading signal research and execution simulation
- Reinforcement-learning portfolio allocation
- SEC filing retrieval and financial RAG
- Evidence-grounded investment reporting
- Production API and web deployment
- Automated testing and validation

The system is intentionally modular. Calculation, prediction, retrieval and language-model explanation are kept separate so that one layer cannot silently replace another.

---

# 2. Architecture

```text
                    ┌─────────────────────────────┐
                    │        React / TypeScript    │
                    │        Portfolio Web UI      │
                    └──────────────┬──────────────┘
                                   │ HTTP / JSON
                    ┌──────────────▼──────────────┐
                    │          FastAPI             │
                    │       REST API Layer         │
                    └──────────────┬──────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────┐
          │                        │                         │
          ▼                        ▼                         ▼
   Quantitative Engine       Research / RAG             Data Layer
          │                        │                         │
  ┌───────┼────────┐       ┌───────┼────────┐        ┌──────┼──────┐
  │       │        │       │       │        │        │      │      │
Returns Risk Optimization  SEC   Chunking Retrieval PostgreSQL Yahoo
Backtest Factors Derivatives     Embeddings Reporting pgvector  CSV
Fixed Income Trading RL
```

### Architectural principles

1. **Deterministic calculations** are implemented in Python modules and exposed through APIs.
2. **Historical data** is processed chronologically to reduce leakage risk.
3. **Optimization constraints** are validated before numerical optimization.
4. **Backtests** include transaction costs, turnover and execution assumptions.
5. **RAG** retrieves evidence from source documents before generating explanations.
6. **LLMs do not determine portfolio weights or replace numerical calculations.**
7. **Production APIs are independently testable without depending on the frontend.**
8. **Frontend and backend are deployable independently.**

---

# 3. Technology Stack

## Backend

- Python 3.12
- FastAPI
- Pydantic
- NumPy
- Pandas
- SciPy
- scikit-learn
- statsmodels
- arch
- CVXPY / PyPortfolioOpt where applicable
- yfinance
- psycopg
- pgvector
- PostgreSQL
- PyPDF
- BeautifulSoup
- pytest
- Ruff

## Frontend

- React
- TypeScript
- Vite
- React Router
- ESLint
- CSS

## Data and Research

- Yahoo Finance adapter
- Local CSV ingestion
- SEC EDGAR filings
- PostgreSQL + pgvector
- Deterministic embedding provider for reproducible development/testing
- Hybrid semantic + lexical retrieval

## Deployment

- Render Web Service
- Render PostgreSQL
- Vercel
- Native Python runtime
- No Docker dependency

---

# 4. Development Stages

## Stage 1 — Foundation and Architecture

Established the initial application structure, backend/frontend separation, configuration system, API foundation, testing setup and development conventions.

### Main components

- FastAPI application
- React frontend
- API routing
- Configuration management
- Health endpoints
- Testing framework
- Development documentation

### Purpose

Create a stable foundation before implementing financial functionality.

---

## Stage 2 — Market Data Architecture

Implemented a provider-based market-data pipeline:

```text
Provider
   ↓
Ingestion
   ↓
Normalization
   ↓
Validation
   ↓
Dataset Store
```

### Providers

- Deterministic mock provider
- Local CSV provider
- Yahoo Finance adapter

### Validation

Market data is checked for:

- Required columns
- Date ordering
- Missing values
- Duplicate timestamps
- OHLC consistency
- Numeric validity

This creates a reproducible boundary between external data and the quantitative engine.

---

## Stage 3 — Returns and Portfolio Analytics

Implemented the core mathematical portfolio analytics layer.

### Return calculations

Simple return:

\[
R_t = \frac{P_t}{P_{t-1}} - 1
\]

Log return:

\[
r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)
\]

Cumulative return:

\[
R_{cum} = \prod_{t=1}^{T}(1+R_t)-1
\]

Annualized return:

\[
R_{ann}=(1+R_{cum})^{\frac{N}{252}}-1
\]

Annualized volatility:

\[
\sigma_{ann}=\sigma_{daily}\sqrt{252}
\]

Sharpe ratio:

\[
Sharpe=\frac{R_p-R_f}{\sigma_p}
\]

Portfolio expected return:

\[
E[R_p]=w^T\mu
\]

Portfolio variance:

\[
\sigma_p^2=w^T\Sigma w
\]

Portfolio volatility:

\[
\sigma_p=\sqrt{w^T\Sigma w}
\]

Maximum drawdown is calculated from the running portfolio peak.

---

## Stage 4 — Risk Analytics

Implemented classical portfolio risk metrics.

### Value at Risk

Historical VaR at confidence level \(c\):

\[
VaR_c=-Q_{1-c}(R)
\]

Parametric VaR:

\[
VaR_c=-(\mu+z_{1-c}\sigma)
\]

Expected Shortfall:

\[
ES_c=-E[R\mid R\le Q_{1-c}(R)]
\]

### Additional metrics

- Downside volatility
- Sortino ratio
- Beta
- Tracking error
- Concentration
- Marginal Risk Contribution
- Component Risk Contribution
- Percentage Risk Contribution

Marginal contribution to portfolio volatility is based on:

\[
MRC_i=\frac{(\Sigma w)_i}{\sigma_p}
\]

Component risk contribution:

\[
CRC_i=w_iMRC_i
\]

---

## Stage 5 — Classical Portfolio Optimization

Implemented:

- Equal Weight
- Minimum Volatility
- Maximum Sharpe
- Risk Parity

General constrained optimization:

\[
\min_w f(w)
\]

subject to:

\[
\sum_iw_i=1
\]

and:

\[
w_{min}\le w_i\le w_{max}
\]

### Maximum Sharpe

\[
\max_w
\frac{w^T\mu-R_f}
{\sqrt{w^T\Sigma w}}
\]

### Risk Parity

The objective attempts to balance portfolio risk contributions rather than simply capital weights.

Numerical optimization uses constrained SLSQP with validation of covariance matrices, bounds and final weights.

---

## Stage 6 — Efficient Frontier

Implemented target-return portfolio optimization and efficient-frontier generation.

Typical problem:

\[
\min_w w^T\Sigma w
\]

subject to:

\[
w^T\mu=R_{target}
\]

\[
\sum_iw_i=1
\]

and portfolio bounds.

The frontier is generated only across the feasible return range under the selected constraints.

---

## Stage 7 — Historical Backtesting

Implemented a chronological portfolio backtesting engine.

### Features

- Initial capital
- Portfolio weights
- Rebalancing
- Daily/weekly/monthly schedules
- Transaction costs
- Turnover
- Equity curve
- Portfolio returns
- Drawdown
- Performance summary

Approximate portfolio wealth evolution:

\[
V_t=V_{t-1}(1+R_{p,t})-C_t
\]

where \(C_t\) represents transaction costs.

The engine deliberately avoids future information when determining historical portfolio decisions.

---

## Stage 8 — Quantitative FastAPI

Exposed the core financial engine through REST APIs.

Representative endpoints:

```text
/quant/returns
/quant/risk
/quant/optimize
/quant/frontier
/quant/backtest
/quant/concentration
```

The API layer provides validation and a stable interface between the numerical engine and frontend.

---

## Stage 9 — Professional React Frontend

Built the first professional web interface.

### Main frontend technologies

- React
- TypeScript
- Vite
- React Router
- CSS
- Typed API client

The frontend was designed as a dashboard rather than a collection of isolated demonstrations.

---

## Stage 10 — Frontend / Backend Integration

Connected the React application to the FastAPI quantitative services.

Implemented:

- API client
- Typed responses
- Health state
- Production API configuration
- Live quantitative metrics

The frontend now consumes backend calculations rather than duplicating financial logic.

---

## Stage 11 — Interactive Portfolio Builder and Optimization

Added interactive portfolio construction.

Users can provide:

- Assets
- Expected returns
- Covariance assumptions
- Risk-free rate
- Minimum weights
- Maximum weights

The system then compares the classical optimization methods.

The frontend explicitly separates **market-derived inputs** from **user assumptions**, avoiding accidental replacement of assumptions with historical averages.

---

## Stage 12 — Real Historical Portfolio Data

Connected portfolio analytics to real historical market data.

The workflow aligns asset prices by date and derives:

```text
Adjusted prices
     ↓
Aligned observations
     ↓
Asset returns
     ↓
Expected returns / covariance
     ↓
Portfolio analytics
```

The architecture also preserves the possibility of replacing Yahoo Finance with another validated provider.

---

## Stage 13 — Risk Analytics Dashboard

Built a dedicated risk dashboard displaying:

- Volatility
- Downside volatility
- Sharpe ratio
- Sortino ratio
- Historical VaR
- Parametric VaR
- Expected Shortfall
- Maximum Drawdown

The dashboard consumes the same backend risk engine used by the API.

---

## Stage 14 — Historical Risk Data Integration

Replaced demonstration risk values with real historical portfolio returns.

The dashboard therefore reflects the actual selected historical portfolio data rather than static sample numbers.

---

## Stage 15 — Efficient Frontier Dashboard

Connected the efficient-frontier engine to the React frontend.

The UI displays the feasible portfolio risk/return relationship and portfolio statistics generated by the backend.

Constraint-aware frontier calculations ensure that target returns outside the feasible range are rejected.

---

## Stage 16 — Historical Backtesting Dashboard

Connected the backtesting engine to the live market-data pipeline.

The dashboard reports:

- Final capital
- Cumulative return
- Annualized return
- Volatility
- Maximum drawdown
- Turnover
- Transaction costs
- Equity curve

The equity curve is generated directly from the backend backtest result.

---

## Stage 17 — Reinforcement Learning Portfolio Management

Implemented a first RL portfolio-management framework using tabular Q-learning.

### Environment

The environment represents:

- Portfolio state
- Market observations
- Previous allocation/action
- Portfolio reward

### Reward structure

A simplified reward can be represented as:

\[
Reward_t =
R_{portfolio,t}
-Cost_t
-\lambda_{risk}RiskPenalty_t
-\lambda_{turnover}Turnover_t
-\lambda_{drawdown}DrawdownPenalty_t
\]

### Important design choice

The first implementation uses a discrete action space rather than immediately applying a complex continuous-control algorithm.

The system supports comparison with classical portfolio approaches rather than assuming that RL produces superior investment performance.

---

# 5. Stage 18 — AI Research Copilot

Introduced the research architecture:

```text
Financial Documents
       ↓
Document Ingestion
       ↓
Chunking
       ↓
Embeddings
       ↓
Vector Store
       ↓
Retrieval
       ↓
Evidence
       ↓
LLM Explanation / Report
```

The AI layer is deliberately separated from the quantitative engine.

### Guardrail

The LLM is not the source of truth for:

- Portfolio weights
- Returns
- Risk metrics
- Pricing calculations
- Backtest results

Those values must come from deterministic financial calculations.

---

# 6. Stage 19 — Production Financial RAG

Stage 19 was developed as a series of production-oriented components.

## 19A — Real SEC Corpus

Added primary-source SEC filings:

- Apple 2025 Form 10-K
- Microsoft FY2025 Form 10-K
- NVIDIA FY2025 Form 10-K

The corpus contains document metadata such as:

- Company
- Ticker
- Document type
- Publication date
- Source

---

## 19B — Section-Aware Chunking

Documents are divided into meaningful sections rather than arbitrary text blocks.

Default configuration:

```text
Chunk size: 500
Overlap:    75
```

This improves retrieval quality while preserving financial context.

---

## 19C — Embedding Architecture

Introduced an `EmbeddingProvider` abstraction.

A deterministic hash-based embedding provider is used for reproducible development/testing.

The architecture allows a production embedding model to be introduced without rewriting the retrieval layer.

---

## 19D — PostgreSQL + pgvector

Implemented vector storage directly inside PostgreSQL using pgvector.

Benefits:

- Relational metadata
- Vector similarity
- Single database
- Easier deployment
- No separate vector database dependency

---

## 19E — Semantic Retrieval

Implemented semantic retrieval with metadata filtering.

Supported filters include:

- Company
- Ticker
- Document type
- Publication cutoff
- Section

This allows historically controlled research queries.

---

## 19F — Hybrid Retrieval and Evaluation

Combined:

- Semantic similarity
- Lexical relevance

The resulting ranking combines both signals rather than relying on vector similarity alone.

Evaluation utilities include:

- Precision@K
- Recall@K
- Mean Reciprocal Rank

---

## 19G — Real SEC Retrieval Evaluation

Validated retrieval against the real SEC corpus using historical document cutoffs and metadata filters.

This is important for preventing future documents from leaking into historical research questions.

---

## 19H — Production RAG API

Added retrieval endpoints for semantic/hybrid financial research.

Example workflow:

```text
Question
  ↓
Ticker / metadata filter
  ↓
Hybrid retrieval
  ↓
Ranked evidence
  ↓
Source-aware response
```

---

## 19I — Automated Corpus Indexing

Implemented an automated corpus indexer that:

1. Builds the corpus
2. Removes previous versions of documents
3. Generates embeddings
4. Inserts chunks
5. Preserves metadata

The production SEC corpus currently contains approximately **495 indexed chunks**.

---

## 19J — Production RAG Smoke Pipeline

Added a reproducible smoke workflow that indexes the corpus and verifies retrieval through the API.

Production verification successfully retrieves AAPL evidence from the Apple 2025 Form 10-K.

---

# 7. Stage 20 — Time-Series and Factor Models

Implemented:

- ARIMA
- GARCH
- CAPM
- Fama-French style factor analysis

## CAPM

\[
R_i-R_f=\alpha_i+\beta_i(R_m-R_f)+\epsilon_i
\]

The model estimates:

- Alpha
- Beta
- Residual behaviour
- Model fit

## Fama-French

The factor regression is represented generally as:

\[
R_i-R_f=
\alpha+
\beta_M(MKT-R_f)+
\beta_S SMB+
\beta_H HML+
\epsilon
\]

where:

- \(MKT-R_f\) = market excess return
- \(SMB\) = size factor
- \(HML\) = value factor

## ARIMA

ARIMA models a time series using autoregressive, differencing and moving-average components:

\[
ARIMA(p,d,q)
\]

## GARCH

A basic GARCH(1,1) variance specification is:

\[
\sigma_t^2=
\omega+
\alpha\epsilon_{t-1}^2+
\beta\sigma_{t-1}^2
\]

These models are treated as research/forecasting tools, not guaranteed prediction systems.

---

# 8. Stage 21 — Advanced Risk

Implemented:

- Monte Carlo VaR
- Stress testing
- Scenario analysis
- Factor risk
- Risk attribution

Monte Carlo risk estimates the distribution of future portfolio outcomes through simulated returns.

Stress testing evaluates portfolio behaviour under explicit adverse scenarios rather than relying only on historical observations.

Factor risk decomposes portfolio exposure into systematic sources of risk.

Risk attribution identifies which positions or factors contribute most to overall portfolio risk.

---

# 9. Stage 22 — Derivatives

Implemented pricing and analytics for:

- Forwards
- Futures
- Put-call parity
- Black-Scholes options
- Greeks
- Binomial options
- Implied volatility

## Forward pricing

For a simple non-income asset:

\[
F_0=S_0e^{rT}
\]

With continuous dividend yield \(q\):

\[
F_0=S_0e^{(r-q)T}
\]

## Put-call parity

\[
C-P=S_0-Ke^{-rT}
\]

for a non-dividend-paying underlying.

## Black-Scholes call

\[
C=S_0N(d_1)-Ke^{-rT}N(d_2)
\]

where:

\[
d_1=
\frac{\ln(S_0/K)+(r+\frac{1}{2}\sigma^2)T}
{\sigma\sqrt{T}}
\]

\[
d_2=d_1-\sigma\sqrt{T}
\]

The implementation also calculates option Greeks such as:

- Delta
- Gamma
- Vega
- Theta
- Rho

---

# 10. Stage 23 — Fixed Income

Implemented:

- Bond pricing
- Yield to maturity
- Duration
- Modified duration
- Convexity
- Yield curves
- Interest-rate sensitivity

## Bond price

\[
P=
\sum_{t=1}^{n}
\frac{C_t}{(1+y)^t}
+
\frac{F}{(1+y)^n}
\]

## Approximate duration-based price sensitivity

\[
\frac{\Delta P}{P}
\approx
-D_{mod}\Delta y
\]

## Convexity adjustment

\[
\frac{\Delta P}{P}
\approx
-D_{mod}\Delta y+
\frac{1}{2}Convexity(\Delta y)^2
\]

These measures provide a basic framework for understanding fixed-income price sensitivity to interest-rate changes.

---

# 11. Stage 24 — Systematic Trading Research

Implemented:

- Momentum signals
- Mean-reversion signals
- Position sizing
- Walk-forward research
- Execution simulation
- Slippage assumptions
- Transaction costs
- Out-of-sample evaluation

The research pipeline separates:

```text
Signal generation
      ↓
Position sizing
      ↓
Execution assumptions
      ↓
Portfolio returns
      ↓
Performance evaluation
```

This separation prevents trading signals from being mixed with execution assumptions.

---

# 12. Stage 25 — Reporting

Implemented structured financial reporting for:

- Research
- Portfolio analysis
- Risk analysis
- Grounded investment research

Reports preserve evidence references so that narrative conclusions can be traced back to retrieved financial documents.

---

# 13. Stage 26 — Production Hardening

Added:

- Production configuration
- Request bounds
- Environment validation
- Readiness checks
- Production workflow
- API safety checks
- RAG workflow validation

The production system distinguishes development and production environments.

---

# 14. Stage 27 — Professional Web Application

Integrated the completed backend capabilities into the React interface.

Main application areas include:

```text
Dashboard
Portfolio
Optimization
Frontier
Risk
Backtest
Research
RL
```

The frontend communicates with the FastAPI backend through typed API services.

The Research interface connects the production RAG workflow to the web application.

---

# 15. Stage 28 — Production Deployment and Reproducibility

The final deployment architecture uses:

```text
Vercel
   │
   │ React / TypeScript
   ▼
Render Web Service
   │
   │ FastAPI
   ▼
Render PostgreSQL
   │
   └── pgvector
```

### Production characteristics

- Python 3.12 runtime
- PostgreSQL with pgvector
- FastAPI API
- Vercel frontend
- Render backend
- Environment variables for configuration
- CORS configuration
- Health endpoint
- Readiness endpoint
- Production RAG corpus
- No Docker requirement

### Production checks

The deployed application has been validated through:

- Backend unit/integration tests
- Ruff
- Frontend ESLint
- TypeScript compilation
- Vite production build
- Production health check
- Production readiness check
- Live RAG retrieval test

---

# 16. Testing and Validation

The project follows:

```text
Implement
   ↓
Unit tests
   ↓
Integration tests
   ↓
Lint
   ↓
Production build
   ↓
API smoke tests
   ↓
Regression validation
```

The backend test suite has been used throughout development to validate financial calculations and API behaviour.

The final validation included:

- **251 backend tests passing**
- Ruff passing
- ESLint passing
- TypeScript passing
- Vite production build passing
- Production health passing
- Production readiness passing
- Live RAG retrieval returning 5 evidence results

Two existing dependency deprecation warnings from FastAPI/Starlette/httpx were observed during testing; they do not represent test failures.

---

# 17. Data Leakage and Backtesting Controls

Financial machine-learning and backtesting systems are particularly vulnerable to look-ahead bias.

Portfolio Master therefore uses chronological thinking throughout the system.

### Principles

- Historical observations precede decisions.
- Training data precedes validation/test data.
- Backtest calculations do not use future portfolio information.
- Walk-forward evaluation preserves temporal order.
- Research retrieval supports publication-date cutoffs.
- Future SEC filings should not be used when evaluating a historical information set.

A strong numerical result is not considered meaningful if it was produced using information that would not have been available at the time.

---

# 18. Production RAG Example

A production research query can be structured as:

```json
{
  "query": "Apple risk factors and business risks",
  "ticker": "AAPL",
  "published_before": "2025-12-31",
  "method": "hybrid",
  "top_k": 5
}
```

The production system successfully returned five evidence chunks from:

```text
Apple Inc. 2025 Form 10-K
SEC EDGAR
Published: 2025-10-31
Section: Item 1A. Risk Factors
```

This demonstrates the complete path:

```text
User question
    ↓
FastAPI
    ↓
Metadata filtering
    ↓
Hybrid retrieval
    ↓
PostgreSQL / pgvector
    ↓
Ranked evidence
    ↓
Frontend research interface
```

---

# 19. Important Financial/Data Disclaimer

Portfolio Master is a **technical, educational and demonstration project**.

The calculations and research workflows are intended to demonstrate quantitative-finance engineering, financial modelling, software architecture and investment-research workflows.

They should **not** be interpreted as:

- Financial advice
- Investment advice
- A recommendation to buy or sell securities
- A guarantee of investment performance
- A prediction of future market returns
- A substitute for professional financial, accounting, legal or tax advice

Results depend heavily on the quality, frequency, survivorship characteristics and historical availability of the input data.

Users should use appropriate, validated and licensed financial data for any real-world application. Market-data provider terms, exchange licensing requirements and regulatory obligations must be considered before commercial use.

Historical backtest performance does not guarantee future results.

The SEC corpus and research examples are used for technical demonstration and should not be treated as a complete representation of all information available about a company.

---

# 20. Known Limitations

The platform is intentionally a portfolio/academic engineering system rather than a production institutional trading system.

Potential extensions include:

- Larger historical datasets
- Institutional market-data providers
- Point-in-time fundamentals
- Corporate-action handling across multiple vendors
- More sophisticated execution models
- Market-impact models
- Portfolio constraints such as sector and factor limits
- Continuous-action RL
- Additional factor datasets
- Alternative asset classes
- Stronger model-selection procedures
- More extensive statistical validation
- Production-grade authentication and authorization
- Monitoring and observability
- Dedicated background workers
- Larger-scale vector retrieval
- Production LLM providers with enterprise controls

These are extensions rather than requirements for the current demonstration platform.

---

# 21. Repository Structure

```text
portfolio-master/
│
├── backend/
│   ├── app/
│   │   ├── analytics/
│   │   ├── api/
│   │   ├── backtest/
│   │   ├── core/
│   │   ├── data/
│   │   ├── derivatives/
│   │   ├── fixed_income/
│   │   ├── optimization/
│   │   ├── research/
│   │   ├── risk/
│   │   ├── rl/
│   │   ├── schemas/
│   │   └── trading/
│   │
│   └── tests/
│
├── frontend/
│   ├── src/
│   └── ...
│
├── data/
├── docs/
├── notebooks/
├── scripts/
├── .env.example
├── .gitignore
├── LICENSE
├── pytest.ini
└── README.md
```

---

# 22. Professional Use of the Project

Portfolio Master demonstrates practical knowledge across three connected areas:

### Quantitative Finance

- Portfolio theory
- Risk
- Optimization
- Derivatives
- Fixed income
- Factor models
- Time-series analysis
- Backtesting
- Systematic trading

### Software Engineering

- API architecture
- Data pipelines
- Testing
- Validation
- PostgreSQL
- Vector databases
- React/TypeScript
- Production deployment

### AI / Research

- Document ingestion
- Embeddings
- Semantic retrieval
- Hybrid search
- RAG
- Evidence grounding
- Financial research automation

The objective is not simply to demonstrate individual algorithms, but to show how they can be integrated into a coherent investment-technology workflow.

---

# 23. Author

## Om Barot

**B.Tech Computer Science & Engineering — VIT Vellore, 2026**

**MSc International Accounting & Finance — Bayes Business School, City St George's, University of London, 2026–27**

Portfolio Master was developed to combine a computer-science engineering background with quantitative finance, financial modelling and investment research.

The project reflects an interest in building practical systems at the intersection of:

**Quantitative Finance × Software Engineering × Data Science × AI**

---

# 24. Final Project Summary

Portfolio Master is a full-stack quantitative investment research platform that brings together deterministic financial analytics, portfolio construction, risk management, historical simulation, systematic research, reinforcement learning and evidence-grounded financial AI.

Its central design principle is:

> **Use mathematics and validated data for financial truth, and use AI to improve research, retrieval and explanation around that truth.**

That separation is intended to make the platform more transparent, testable and suitable for continued academic and professional development.
