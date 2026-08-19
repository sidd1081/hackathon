const COLORS = {
  slate: "bg-slate-100 text-slate-700 ring-slate-500/20",
  indigo: "bg-indigo-50 text-indigo-700 ring-indigo-600/20",
  emerald: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  amber: "bg-amber-50 text-amber-700 ring-amber-600/20",
  rose: "bg-rose-50 text-rose-700 ring-rose-600/20",
};

export function Badge({ color = "slate", className = "", children }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${COLORS[color]} ${className}`}
    >
      {children}
    </span>
  );
}

const CONFIDENCE = {
  high: ["emerald", "High"],
  medium: ["amber", "Medium"],
  low: ["rose", "Low"],
};

export function ConfidenceBadge({ level }) {
  const key = String(level || "").toLowerCase();
  const [color, label] = CONFIDENCE[key] || ["slate", level || "Unknown"];
  return <Badge color={color}>Confidence: {label}</Badge>;
}
