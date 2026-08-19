export function EmptyState({ title, message, icon }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-slate-200 bg-slate-50/60 px-6 py-10 text-center">
      <div className="mb-3 text-slate-300">{icon || <DefaultIcon />}</div>
      <p className="text-sm font-medium text-slate-600">{title}</p>
      {message && (
        <p className="mt-1 max-w-sm text-sm text-slate-400">{message}</p>
      )}
    </div>
  );
}

function DefaultIcon() {
  return (
    <svg
      className="h-8 w-8"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12h6m-6 4h6m2 5H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h7l5 5v11a2 2 0 0 1-2 2z"
      />
    </svg>
  );
}
