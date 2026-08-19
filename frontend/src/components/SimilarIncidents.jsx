import { Section } from "./ui/Card.jsx";
import { Alert } from "./ui/Alert.jsx";
import { EmptyState } from "./ui/EmptyState.jsx";
import { DataBadge } from "./ui/Pills.jsx";
import { IncidentCard } from "./IncidentCard.jsx";

export function SimilarIncidents({ analysis }) {
  const { status, data, error } = analysis;
  const supportingIds = new Set(
    (data?.supporting_incidents || []).map((s) => s.ticket_id),
  );

  return (
    <Section
      label="Historical Evidence"
      title="Similar Historical Incidents"
      description="Actual records retrieved from the indexed dataset (FAISS search + rerank). These are facts, not model output — the AI analysis above is derived from them."
      accent="slate"
      tag={<DataBadge />}
    >
      {status === "idle" && (
        <EmptyState
          title="No analysis yet"
          message="Similar historical incidents will appear here after you analyze an incident."
        />
      )}

      {status === "loading" && <SkeletonList />}

      {status === "error" && (
        <Alert variant="error" title="Could not retrieve incidents">
          {error}
        </Alert>
      )}

      {status === "success" &&
        (data.similar_incidents?.length ? (
          <div className="space-y-3">
            {data.similar_incidents.map((incident) => (
              <IncidentCard
                key={incident.ticket_id}
                incident={incident}
                cited={supportingIds.has(incident.ticket_id)}
              />
            ))}
          </div>
        ) : (
          <EmptyState
            title="No similar incidents found"
            message="The index returned no matches for this incident."
          />
        ))}
    </Section>
  );
}

function SkeletonList() {
  return (
    <div className="space-y-3">
      {[0, 1, 2].map((i) => (
        <div key={i} className="animate-pulse rounded-lg border border-slate-200 p-4">
          <div className="mb-3 flex items-center justify-between">
            <div className="h-4 w-28 rounded bg-slate-200" />
            <div className="h-1.5 w-24 rounded-full bg-slate-100" />
          </div>
          <div className="h-3 w-full rounded bg-slate-100" />
          <div className="mt-1.5 h-3 w-2/3 rounded bg-slate-100" />
        </div>
      ))}
    </div>
  );
}
