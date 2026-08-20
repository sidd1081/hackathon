import { useRef, useState } from "react";
import { Section } from "./ui/Card.jsx";
import { Button } from "./ui/Button.jsx";
import { Alert } from "./ui/Alert.jsx";
import { Badge } from "./ui/Badge.jsx";

export function DatasetPanel({ state, onUpload }) {
  const inputRef = useRef(null);
  const [fileName, setFileName] = useState("");
  const busy = state.status === "uploading";

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    setFileName(file ? file.name : "");
  };

  const handleSubmit = () => {
    const file = inputRef.current?.files?.[0];
    if (file) onUpload(file);
  };

  return (
    <Section
      label="Dataset"
      title="Historical Incident Data"
      description="Upload a CSV to clean, embed, and rebuild the search index."
    >
      <div className="space-y-4">
        <div className="flex flex-col gap-3">
          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            onChange={handleChange}
            className="block w-full text-sm text-slate-500 file:mr-3 file:rounded-lg file:border-0 file:bg-indigo-50 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-indigo-700 hover:file:bg-indigo-100"
          />
          <Button
            onClick={handleSubmit}
            loading={busy}
            disabled={!fileName || busy}
          >
            Upload &amp; Index
          </Button>
        </div>

        {state.status === "idle" && (
          <p className="text-sm text-slate-500">
            Required columns:{" "}
            <code className="rounded bg-slate-100 px-1 py-0.5 text-xs text-slate-700">
              ticket_id, project, summary, description, root_cause,
              resolution_status, resolution_notes
            </code>
          </p>
        )}

        {busy && (
          <p className="text-sm text-slate-500">
            Validating, cleaning, embedding and indexing…
          </p>
        )}

        {state.status === "error" && (
          <Alert variant="error" title="Upload failed">
            {state.error}
          </Alert>
        )}

        {state.status === "success" && state.data && (
          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
            <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-slate-700">
              <Badge color="emerald">Indexed</Badge>
              <span>
                <strong className="tabular-nums">{state.data.records}</strong>{" "}
                incidents
              </span>
              <Dot />
              <span className="tabular-nums">
                {state.data.duplicates_removed} duplicates removed
              </span>
              <Dot />
              <span>dim {state.data.embedding_dimension}</span>
              <Dot />
              <span>index: {state.data.index_status}</span>
            </div>
          </div>
        )}
      </div>
    </Section>
  );
}

function Dot() {
  return <span className="text-slate-300">•</span>;
}
