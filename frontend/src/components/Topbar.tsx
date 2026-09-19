export function Topbar() {
  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">QUANTITATIVE INVESTMENT PLATFORM</div>
        <h1>Portfolio Analytics</h1>
      </div>

      <div className="topbar-actions">
        <button className="icon-button" type="button" aria-label="Notifications">
          N
        </button>
        <div className="profile">
          <div className="avatar">OB</div>
          <div>
            <div className="profile-name">Om Barot</div>
            <div className="profile-role">Research User</div>
          </div>
        </div>
      </div>
    </header>
  );
}
