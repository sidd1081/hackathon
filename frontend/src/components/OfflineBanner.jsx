import { API_BASE_URL } from "../services/api.js";
import { Button } from "./ui/Button.jsx";

export function OfflineBanner({ onRetry, checking = false }) {
  const target = API_BASE_URL || "the backend via the dev proxy (/api)";
  return (
    <div className="mb-6 flex flex-col gap-3 rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p className="font-semibold">Backend unavailable</p>
        <p className="mt-0.5">
          Could not reach {target}. Start it with{" "}
          <code className="rounded bg-rose-100 px-1 py-0.5">
            uv run uvicorn app.main:app --reload
          </code>
          .
        </p>
      </div>
      <Button
        variant="secondary"
        onClick={onRetry}
        loading={checking}
        className="shrink-0"
      >
        Retry
      </Button>
    </div>
  );
}
