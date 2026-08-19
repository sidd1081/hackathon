const MAP = {
  checking: ["bg-slate-300", "text-slate-500", "Checking…", true],
  online: ["bg-emerald-500", "text-emerald-600", "Backend online", false],
  offline: ["bg-rose-500", "text-rose-600", "Backend offline", false],
};

export function HealthIndicator({ status }) {
  const [dot, text, label, pulse] = MAP[status] || MAP.checking;
  return (
    <span className="inline-flex items-center gap-2 text-sm">
      <span
        className={`h-2 w-2 rounded-full ${dot} ${pulse ? "animate-pulse" : ""}`}
      />
      <span className={`font-medium ${text}`}>{label}</span>
    </span>
  );
}
