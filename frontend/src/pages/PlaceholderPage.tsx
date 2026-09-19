interface PlaceholderPageProps {
  title: string;
  description: string;
}

export function PlaceholderPage({
  title,
  description,
}: PlaceholderPageProps) {
  return (
    <section>
      <div className="page-heading">
        <div>
          <h2>{title}</h2>
          <p>{description}</p>
        </div>
      </div>

      <div className="panel placeholder-panel">
        <div className="placeholder-icon">Q</div>
        <h3>Module ready for integration</h3>
        <p>
          The quantitative backend is already structured for this module.
          The interactive interface will be connected in the next stages.
        </p>
      </div>
    </section>
  );
}
