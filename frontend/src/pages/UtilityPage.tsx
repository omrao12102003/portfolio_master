interface UtilityPageProps {
  title: string
  eyebrow: string
  description: string
  items: string[]
}

export default function UtilityPage({
  title,
  eyebrow,
  description,
  items,
}: UtilityPageProps) {
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">{eyebrow}</span>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>

      <div className="utility-grid">
        {items.map((item) => (
          <div className="panel utility-card" key={item}>
            <span>{item}</span>
            <small>Connected to the Portfolio Master quantitative API.</small>
          </div>
        ))}
      </div>
    </>
  )
}
