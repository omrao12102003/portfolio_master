interface ConnectionStatusProps {
  connected: boolean
  loading?: boolean
}

export function ConnectionStatus({
  connected,
  loading = false,
}: ConnectionStatusProps) {
  if (loading) {
    return (
      <div className="connection-status">
        <span className="connection-dot" />
        <span>Checking API...</span>
      </div>
    )
  }

  return (
    <div className="connection-status">
      <span className={`connection-dot ${connected ? "connected" : "disconnected"}`} />
      <span>{connected ? "API Connected" : "API Offline"}</span>
    </div>
  )
}

export default ConnectionStatus
