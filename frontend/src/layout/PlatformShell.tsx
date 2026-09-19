export function PlatformShell() {
  return (
    <div className="page">
      <header className="masthead">
        <p className="eyebrow">Quantitative investment research</p>
        <h1>Portfolio Master</h1>
        <p className="lede">
          The software foundation for this research platform is being initialized.
          Classical portfolio analytics, risk, backtesting, reinforcement learning, and
          document research will be added in later stages.
        </p>
      </header>
      <section className="status" aria-labelledby="status-heading">
        <h2 id="status-heading">Current stage</h2>
        <p>Stage 1A — architecture and development environment.</p>
        <p className="note">
          This shell does not display portfolio data, simulated performance, or generated
          research. No investment engine is connected yet.
        </p>
      </section>
    </div>
  );
}
