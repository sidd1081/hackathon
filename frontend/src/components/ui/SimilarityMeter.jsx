export function SimilarityMeter({ value }) {
  const v = Math.max(0, Math.min(1, Number(value) || 0));
  const pct = Math.round(v * 100);
  const color =
    v >= 0.6 ? "bg-emerald-500" : v >= 0.4 ? "bg-amber-500" : "bg-slate-400";

  return (
    <div
      className="flex items-center gap-2"
      title={`Similarity ${v.toFixed(4)}`}
    >
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <span className="tabular-nums text-xs font-medium text-slate-500">
        {v.toFixed(2)}
      </span>
    </div>
  );
}
