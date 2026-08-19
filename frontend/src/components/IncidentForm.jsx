import { Section } from "./ui/Card.jsx";
import { Button } from "./ui/Button.jsx";
import { EXAMPLE_INCIDENT } from "../lib/constants.js";

export function IncidentForm({ value, onChange, onAnalyze, loading }) {
  const isEmpty = !value.trim();

  return (
    <Section
      label="New Incident"
      title="Describe the Incident"
      actions={
        <button
          type="button"
          onClick={() => onChange(EXAMPLE_INCIDENT)}
          className="text-xs font-medium text-indigo-600 hover:text-indigo-500"
        >
          Use example
        </button>
      }
    >
      <div className="space-y-3">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          rows={8}
          placeholder="e.g. Kafka consumers stopped processing messages after a broker restart…"
          className="w-full resize-y rounded-lg border border-slate-300 p-3 text-sm text-slate-800 shadow-sm placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/30"
        />
        <div className="flex items-center justify-between">
          <p className="text-xs text-slate-400 tabular-nums">
            {value.trim().length} characters
          </p>
          <Button onClick={onAnalyze} loading={loading} disabled={isEmpty || loading}>
            Analyze Incident
          </Button>
        </div>
      </div>
    </Section>
  );
}
