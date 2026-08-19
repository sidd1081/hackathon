import { useState } from "react";
import { Header } from "./components/Header.jsx";
import { HealthIndicator } from "./components/HealthIndicator.jsx";
import { OfflineBanner } from "./components/OfflineBanner.jsx";
import { DatasetPanel } from "./components/DatasetPanel.jsx";
import { IncidentForm } from "./components/IncidentForm.jsx";
import { RcaSummary } from "./components/RcaSummary.jsx";
import { SimilarIncidents } from "./components/SimilarIncidents.jsx";
import { useBackendHealth } from "./hooks/useBackendHealth.js";
import { analyzeIncident, uploadDataset } from "./services/api.js";

const IDLE = { status: "idle", data: null, error: null, latencyMs: null };

export default function App() {
  const [incidentText, setIncidentText] = useState("");
  const [analysis, setAnalysis] = useState(IDLE);
  const [dataset, setDataset] = useState(IDLE);
  const backend = useBackendHealth();

  const handleAnalyze = async () => {
    if (!incidentText.trim()) return;
    setAnalysis({ status: "loading", data: null, error: null, latencyMs: null });
    const startedAt = performance.now();
    try {
      const data = await analyzeIncident(incidentText.trim());
      const latencyMs = Math.round(performance.now() - startedAt);
      setAnalysis({ status: "success", data, error: null, latencyMs });
    } catch (err) {
      setAnalysis({ status: "error", data: null, error: err.message, latencyMs: null });
    }
  };

  const handleUpload = async (file) => {
    setDataset({ status: "uploading", data: null, error: null });
    try {
      const data = await uploadDataset(file);
      setDataset({ status: "success", data, error: null });
    } catch (err) {
      setDataset({ status: "error", data: null, error: err.message });
    }
  };

  const analyzing = analysis.status === "loading";

  return (
    <div className="min-h-screen bg-slate-50">
      <Header right={<HealthIndicator status={backend.status} />} />

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:py-8">
        {backend.status === "offline" && (
          <OfflineBanner onRetry={backend.recheck} />
        )}

        <div className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-6 lg:col-span-1">
            <DatasetPanel state={dataset} onUpload={handleUpload} />
            <IncidentForm
              value={incidentText}
              onChange={setIncidentText}
              onAnalyze={handleAnalyze}
              loading={analyzing}
            />
          </div>

          <div className="space-y-6 lg:col-span-2">
            <RcaSummary analysis={analysis} />
            <SimilarIncidents analysis={analysis} />
          </div>
        </div>
      </main>

      <footer className="mx-auto max-w-6xl px-4 pb-8 pt-2 text-center text-xs text-slate-400 sm:px-6">
        Evidence-grounded RCA · never fabricates a root cause · API keys stay
        server-side.
      </footer>
    </div>
  );
}
