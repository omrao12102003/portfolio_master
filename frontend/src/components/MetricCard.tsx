interface MetricCardProps {
  label: string
  value: string
  detail?: string
}

export default function MetricCard({
  label,
  value,
  detail,
}: MetricCardProps) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  )
}
