export function Card({ className = "", children }) {
  return (
    <div
      className={`rounded-xl border border-slate-200 bg-white shadow-sm ${className}`}
    >
      {children}
    </div>
  );
}

const ACCENTS = {
  indigo: "border-l-4 border-l-indigo-500",
  slate: "border-l-4 border-l-slate-300",
};

const LABEL_TONES = {
  indigo: "text-indigo-600",
  slate: "text-slate-500",
};

/** A Card with a standard section header (label + title + optional actions). */
export function Section({
  label,
  title,
  description,
  actions,
  tag,
  accent,
  className = "",
  children,
}) {
  const accentClass = accent ? ACCENTS[accent] || "" : "";
  const labelTone = accent ? LABEL_TONES[accent] || "text-indigo-600" : "text-indigo-600";
  return (
    <Card className={`${accentClass} ${className}`}>
      <div className="flex items-start justify-between gap-4 border-b border-slate-100 px-5 py-4 sm:px-6">
        <div className="min-w-0">
          {label && (
            <p className={`text-xs font-semibold uppercase tracking-wider ${labelTone}`}>
              {label}
            </p>
          )}
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold text-slate-900">{title}</h2>
            {tag}
          </div>
          {description && (
            <p className="mt-0.5 text-sm text-slate-500">{description}</p>
          )}
        </div>
        {actions ? <div className="shrink-0">{actions}</div> : null}
      </div>
      <div className="px-5 py-5 sm:px-6">{children}</div>
    </Card>
  );
}
