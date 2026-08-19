// Small presentational pills used in section headers.

/** "AI-generated" marker — signals model output, not a stored fact. */
export function AiBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-semibold text-indigo-700 ring-1 ring-inset ring-indigo-600/20">
      <svg className="h-3 w-3" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <path d="M11 2 8.9 7.9 3 10l5.9 2.1L11 18l2.1-5.9L19 10l-5.9-2.1L11 2Zm7 11-1 2.8L14 17l2.9 1.1L18 21l1.1-2.9L22 17l-2.9-1.1L18 13Z" />
      </svg>
      AI-generated
    </span>
  );
}

/** Neutral marker for factual dataset records. */
export function DataBadge() {
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-semibold text-slate-600 ring-1 ring-inset ring-slate-500/20">
      Dataset records
    </span>
  );
}

const TONES = {
  slate: "bg-slate-100 text-slate-600 ring-slate-500/20",
  indigo: "bg-indigo-50 text-indigo-700 ring-indigo-600/20",
  rose: "bg-rose-50 text-rose-700 ring-rose-600/20",
};

/** Generic status pill (optionally pulsing). */
export function StatusPill({ tone = "slate", pulse = false, children }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${TONES[tone]}`}
    >
      {pulse && (
        <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
      )}
      {children}
    </span>
  );
}

/** Client-measured response time (round-trip), honestly labeled. */
export function LatencyPill({ ms }) {
  if (ms == null) return null;
  const label = ms >= 1000 ? `${(ms / 1000).toFixed(1)} s` : `${Math.round(ms)} ms`;
  return (
    <StatusPill tone="slate">
      <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path strokeLinecap="round" d="M12 7v5l3 2" />
      </svg>
      <span title="Client-measured round-trip time">{label}</span>
    </StatusPill>
  );
}
