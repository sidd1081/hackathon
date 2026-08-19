export function Header({ right }) {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-5 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-sm font-bold text-white">
            RCA
          </div>
          <div>
            <h1 className="text-lg font-semibold text-slate-900">
              AI Incident RCA Assistant
            </h1>
            <p className="text-sm text-slate-500">
              Retrieve similar historical incidents and generate
              evidence-grounded root cause analysis.
            </p>
          </div>
        </div>
        {right ? <div className="shrink-0">{right}</div> : null}
      </div>
    </header>
  );
}
