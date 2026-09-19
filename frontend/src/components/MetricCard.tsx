interface MetricCardProps {
  label: string;
  value: string;
  change?: string;
  description?: string;
}

export function MetricCard({
  label,
  value,
  change,
  description,
}: MetricCardProps) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value-row">
        <div className="metric-value">{value}</div>
        {change && <div className="metric-change">{change}</div>}
      </div>
      {description && <div className="metric-description">{description}</div>}
    </div>
  );
}
