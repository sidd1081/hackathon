import { Section } from "./ui/Card.jsx";
import { Badge, ConfidenceBadge } from "./ui/Badge.jsx";
import { AiBadge, LatencyPill, StatusPill } from "./ui/Pills.jsx";
import { Alert } from "./ui/Alert.jsx";
import { EmptyState } from "./ui/EmptyState.jsx";
import { Spinner } from "./ui/Spinner.jsx";
import { NOT_DOCUMENTED } from "../lib/constants.js";

function Block({ label, value }) {
  const undocumented = value === NOT_DOCUMENTED;
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>
      <p
        className={`mt-1 text-sm leading-relaxed ${
          undocumented ? "italic text-amber-700" : "text-slate-700"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function HeaderActions({ status, data, latencyMs }) {
  if (status === "loading") {
    return (
      <StatusPill tone="indigo" pulse>
        Analyzing…
      </StatusPill>
    );
  }
  if (status === "error") {
    return <StatusPill tone="rose">Failed</StatusPill>;
  }
  if (status === "success" && data) {
    return (
      <div className="flex items-center gap-2">
        <LatencyPill ms={latencyMs} />
        <ConfidenceBadge level={data.confidence} />
      </div>
    );
  }
  return null;
}

export function RcaSummary({ analysis }) {
  const { status, data, error, latencyMs } = analysis;
  const undocumented = data && data.root_cause === NOT_DOCUMENTED;

  return (
    <Section
      label="AI Analysis"
      title="Root Cause Analysis"
      description="Synthesized by the LLM from the retrieved historical evidence — not a stored fact."
      accent="indigo"
      tag={<AiBadge />}
      actions={<HeaderActions status={status} data={data} latencyMs={latencyMs} />}
    >
      {status === "idle" && (
        <EmptyState
          title="Awaiting analysis"
          message="Enter an incident and click Analyze Incident to generate an evidence-grounded root cause analysis."
        />
      )}

      {status === "loading" && (
        <div className="space-y-3 py-4">
          <div className="flex items-center gap-3 text-slate-500">
            <Spinner />
            <span className="text-sm">
              Retrieving evidence and generating RCA…
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Pipeline: vector retrieval → rerank → LLM synthesis
          </p>
        </div>
      )}

      {status === "error" && (
        <Alert variant="error" title="Analysis failed">
          {error}
        </Alert>
      )}

      {status === "success" && data && (
        <div className="space-y-5">
          {undocumented && (
            <Alert variant="info">
              No documented root cause could be established from the retrieved
              evidence, so the assistant is not asserting one (it will not
              fabricate a cause).
            </Alert>
          )}

          <Block label="Summary" value={data.summary} />

          <div className="grid gap-5 sm:grid-cols-2">
            <Block label="Likely Root Cause" value={data.root_cause} />
            <Block label="Recommended Resolution" value={data.resolution} />
          </div>

          <div className="border-t border-slate-100 pt-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
              Sources used (historical tickets)
            </p>
            {data.supporting_incidents?.length ? (
              <div className="mt-2 flex flex-wrap gap-2">
                {data.supporting_incidents.map((s) => (
                  <Badge key={s.ticket_id} color="indigo">
                    <span className="font-mono">{s.ticket_id}</span>
                  </Badge>
                ))}
              </div>
            ) : (
              <p className="mt-1 text-sm italic text-slate-400">
                No historical ticket was cited as support.
              </p>
            )}
            <p className="mt-2 text-xs text-slate-400">
              Confidence is the model&rsquo;s self-assessment given the evidence
              — not a statistical probability.
            </p>
          </div>
        </div>
      )}
    </Section>
  );
}
