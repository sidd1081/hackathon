const STYLES = {
  error: "border-rose-200 bg-rose-50 text-rose-800",
  info: "border-slate-200 bg-slate-50 text-slate-700",
  success: "border-emerald-200 bg-emerald-50 text-emerald-800",
};

export function Alert({ variant = "error", title, children }) {
  return (
    <div
      role="alert"
      className={`rounded-lg border px-4 py-3 text-sm ${STYLES[variant]}`}
    >
      {title && <p className="font-semibold">{title}</p>}
      {children && <div className={title ? "mt-0.5" : ""}>{children}</div>}
    </div>
  );
}
