import { useLayoutEffect, useRef, useState } from "react";

/**
 * Clamped text with a "Show more" / "Show less" toggle. The toggle only
 * appears when the text actually overflows the clamp (measured via
 * scrollHeight vs. clientHeight), so short values render with no button.
 */
export function Expandable({ text, clampClass, className = "", emptyText = "—" }) {
  const ref = useRef(null);
  const [expanded, setExpanded] = useState(false);
  const [overflowing, setOverflowing] = useState(false);

  useLayoutEffect(() => {
    const el = ref.current;
    if (!el) return;
    setOverflowing(el.scrollHeight > el.clientHeight + 1);
    // Re-measure only when the text/clamp changes, while still collapsed.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text, clampClass]);

  return (
    <div className="min-w-0">
      <p
        ref={ref}
        className={`break-words ${expanded ? "" : clampClass} ${className}`}
      >
        {text || emptyText}
      </p>
      {overflowing && (
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="mt-0.5 text-xs font-medium text-indigo-600 hover:text-indigo-500"
        >
          {expanded ? "Show less" : "Show more"}
        </button>
      )}
    </div>
  );
}
