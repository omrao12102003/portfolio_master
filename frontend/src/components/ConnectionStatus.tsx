interface ConnectionStatusProps {
  connected: boolean;
  loading?: boolean;
}

export function ConnectionStatus({
  connected,
  loading = false,
}: ConnectionStatusProps) {
  const label = loading
    ? "Connecting..."
    : connected
      ? "API connected"
      : "API offline";

  return (
    <div className="sidebar-footer">
      <span className={`status-dot ${connected ? "connected" : "offline"}`} />
      {label}
    </div>
  );
}
