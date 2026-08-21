/** A simple full-width segmented-control tab bar. */
export function Tabs({ tabs, active, onChange, className = "" }) {
  return (
    <div
      role="tablist"
      className={`flex w-full gap-1 rounded-lg border border-slate-200 bg-slate-100 p-1 ${className}`}
    >
      {tabs.map((t) => {
        const isActive = t.id === active;
        return (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onChange(t.id)}
            className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition ${
              isActive
                ? "bg-white text-indigo-700 shadow-sm"
                : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {t.label}
          </button>
        );
      })}
    </div>
  );
}
