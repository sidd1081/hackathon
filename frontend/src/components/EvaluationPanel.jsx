import { Section } from "./ui/Card.jsx";
import { Badge } from "./ui/Badge.jsx";
import { useEvaluation } from "../hooks/useEvaluation.js";

// --- formatting helpers ------------------------------------------------------
const pct = (v) => (v == null ? "—" : `${Math.round(v * 100)}%`);
const dec = (v) => (v == null ? "—" : Number(v).toFixed(2));
const ms = (v) => (v == null ? "—" : `${Math.round(v)} ms`);

// Status tone from a [0,1] metric. `lowerBetter` flips the polarity (used for
// hallucination rate). Color is paired with the tile label + a meter — never
// color alone.
function toneFor(v, { lowerBetter = false } = {}) {
  if (v == null) return "slate";
  const good = lowerBetter ? v <= 0.05 : v >= 0.8;
  const ok = lowerBetter ? v <= 0.2 : v >= 0.5;
  return good ? "emerald" : ok ? "amber" : "rose";
}

const METER_BG = {
  emerald: "bg-emerald-500",
  amber: "bg-amber-500",
  rose: "bg-rose-500",
  slate: "bg-slate-400",
};

const VALUE_INK = {
  emerald: "text-emerald-700",
  amber: "text-amber-700",
  rose: "text-rose-700",
  slate: "text-slate-900",
};

function Meter({ value, tone }) {
  const v = Math.max(0, Math.min(1, Number(value) || 0));
  return (
    <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-slate-100">
      <div
        className={`h-full rounded-full ${METER_BG[tone] || METER_BG.slate}`}
        style={{ width: `${Math.round(v * 100)}%` }}
      />
    </div>
  );
}

function StatTile({ label, value, tone = "slate", meter = null, hint }) {
  return (
    <div className="min-w-0 rounded-lg border border-slate-200 bg-white p-3">
      <p className="text-xs font-medium leading-tight text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-semibold tabular-nums ${VALUE_INK[tone]}`}>
        {value}
      </p>
      {meter != null ? <Meter value={meter} tone={tone} /> : null}
      {hint ? <p className="mt-1 text-[11px] text-slate-400">{hint}</p> : null}
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          className="animate-pulse rounded-lg border border-slate-200 p-3"
        >
          <div className="h-3 w-20 rounded bg-slate-100" />
          <div className="mt-2 h-6 w-14 rounded bg-slate-200" />
          <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100" />
        </div>
      ))}
    </div>
  );
}

export function EvaluationPanel() {
  const { status, data, error } = useEvaluation();

  const generated =
    data?.generated_at &&
    new Date(data.generated_at).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });

  return (
    <Section
      label="Benchmark"
      title="System Evaluation"
      description="Offline benchmark across a labeled test set — not a per-query score. Measured through the real pipeline: retrieval quality, answer grounding, and latency."
      accent="slate"
      tag={<Badge color="slate">Latest run</Badge>}
    >
      {status === "loading" && <SkeletonGrid />}

      {status === "error" && (
        <p className="text-sm text-slate-500">
          No evaluation results yet. Run{" "}
          <code className="rounded bg-slate-100 px-1 py-0.5 text-xs text-slate-700">
            uv run python -m scripts.evaluate
          </code>{" "}
          to populate this panel.
        </p>
      )}

      {status === "success" && data && (
        <>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            <StatTile
              label="Recall@5"
              value={pct(data.recall_at_5)}
              tone={toneFor(data.recall_at_5)}
              meter={data.recall_at_5}
              hint="correct ticket retrieved"
            />
            <StatTile
              label="MRR"
              value={dec(data.mrr)}
              tone={toneFor(data.mrr)}
              meter={data.mrr}
              hint="mean reciprocal rank"
            />
            <StatTile
              label="Root-cause correctness"
              value={pct(data.root_cause_correctness)}
              tone={toneFor(data.root_cause_correctness)}
              meter={data.root_cause_correctness}
              hint="vs. gold answer"
            />
            <StatTile
              label="Hallucination rate"
              value={pct(data.hallucination_rate)}
              tone={toneFor(data.hallucination_rate, { lowerBetter: true })}
              hint="lower is better"
            />
            <StatTile
              label="Evidence support"
              value={pct(data.evidence_support_rate)}
              tone={toneFor(data.evidence_support_rate)}
              meter={data.evidence_support_rate}
              hint="citations grounded"
            />
            <StatTile
              label="Correct abstention"
              value={pct(data.abstention_correct_rate)}
              tone={toneFor(data.abstention_correct_rate)}
              meter={data.abstention_correct_rate}
              hint="on out-of-domain"
            />
            <StatTile
              label="Retrieval latency"
              value={ms(data.retrieval_latency_ms)}
              hint="mean, FAISS + rerank"
            />
            <StatTile
              label="Embedding latency"
              value={ms(data.embedding_latency_ms)}
              hint="mean, local MiniLM"
            />
          </div>

          <p className="mt-3 text-xs text-slate-400">
            {data.num_cases} case{data.num_cases === 1 ? "" : "s"}
            {data.groq_model ? ` · ${data.groq_model}` : ""}
            {generated ? ` · generated ${generated}` : ""}
          </p>
        </>
      )}
    </Section>
  );
}
