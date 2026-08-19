import { Badge } from "./ui/Badge.jsx";
import { SimilarityMeter } from "./ui/SimilarityMeter.jsx";
import { NOT_DOCUMENTED } from "../lib/constants.js";

function Field({ label, value }) {
  const muted = !value || value === NOT_DOCUMENTED;
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>
      <p className={`mt-0.5 text-sm ${muted ? "italic text-slate-400" : "text-slate-700"}`}>
        {value || "—"}
      </p>
    </div>
  );
}

export function IncidentCard({ incident, cited = false }) {
  return (
    <div className="rounded-lg border border-slate-200 p-4 transition hover:border-slate-300">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-sm font-semibold text-slate-900">
            {incident.ticket_id}
          </span>
          {cited && <Badge color="indigo">Cited by AI</Badge>}
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400">Similarity</span>
          <SimilarityMeter value={incident.similarity} />
        </div>
      </div>

      <p className="mt-2 line-clamp-3 text-sm text-slate-600">
        {incident.description}
      </p>

      <div className="mt-3 grid gap-3 sm:grid-cols-2">
        <Field label="Root cause" value={incident.root_cause} />
        <Field label="Resolution" value={incident.resolution} />
      </div>
    </div>
  );
}
