"""Local-only telemetry collector for CQ Engine MCP Server.

Collects tool invocation events, stores them in daily JSONL files,
and provides summary/aggregation methods. All data stays local.
No network calls. Ever.
"""

import json
import os
import uuid
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# Pattern mapping: tool name keyword -> pattern name
TOOL_PATTERN_MAP: dict[str, str] = {
    "decompose": "Pattern 01: Attention Budget",
    "gate": "Pattern 02: Context Gate",
    "persona": "Pattern 03: Cognitive Profile",
    "mutate": "Pattern 05: Assumption Mutation",
    "learn": "Pattern 06: Experience Distillation",
    "cqlint": "Patterns 01-05 (Quality Linting)",
}


class TelemetryCollector:
    """Local-only telemetry collector. No network calls. Ever."""

    def __init__(self, storage_path: str = "~/.cq-engine/telemetry") -> None:
        self.storage_path = Path(storage_path).expanduser()
        self.storage_path.mkdir(parents=True, exist_ok=True)
        (self.storage_path / "events").mkdir(exist_ok=True)
        (self.storage_path / "aggregates").mkdir(exist_ok=True)
        self._session_id = os.environ.get(
            "CQ_SESSION_ID", str(uuid.uuid4())[:8]
        )

    def _events_dir(self) -> Path:
        """Return the events directory path."""
        return self.storage_path / "events"

    def _event_file(self, date_str: str) -> Path:
        """Return the JSONL file path for a given date string."""
        return self._events_dir() / f"{date_str}.jsonl"

    def emit(self, event_type: str, tool: str, data: dict) -> None:
        """Append a telemetry event to the daily JSONL file.

        Args:
            event_type: Type of event (e.g., "tool_invocation").
            tool: Tool name (e.g., "cq_engine__gate").
            data: Event data dict. If it contains "_duration_ms",
                  that value is extracted and stored as a top-level field.
        """
        # Extract duration from data if present
        duration_ms = data.pop("_duration_ms", None)

        timestamp = datetime.now(timezone.utc).isoformat()
        today_str = date.today().isoformat()

        event = {
            "timestamp": timestamp,
            "event_type": event_type,
            "tool": tool,
            "data": data,
            "session_id": self._session_id,
        }

        if duration_ms is not None:
            event["duration_ms"] = duration_ms

        event_file = self._event_file(today_str)
        try:
            with open(event_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        except OSError:
            # File lock contention or permission error — skip silently
            pass

    def _load_events(self, date_str: str) -> list[dict]:
        """Load all events for a given date."""
        event_file = self._event_file(date_str)
        if not event_file.exists():
            return []
        events = []
        for line in event_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events

    def get_daily_summary(self, date_str: str | None = None) -> dict:
        """Get summary for a specific date.

        Args:
            date_str: Date in YYYY-MM-DD format. Defaults to today.

        Returns:
            Summary dict with total event count and per-tool breakdown.
        """
        if date_str is None:
            date_str = date.today().isoformat()

        events = self._load_events(date_str)

        by_tool: dict[str, dict] = {}
        for event in events:
            tool = event.get("tool", "unknown")
            if tool not in by_tool:
                by_tool[tool] = {"count": 0, "total_duration_ms": 0, "has_duration": False}
            by_tool[tool]["count"] += 1
            duration = event.get("duration_ms")
            if duration is not None:
                by_tool[tool]["total_duration_ms"] += duration
                by_tool[tool]["has_duration"] = True

        # Compute averages and clean up
        by_tool_clean: dict[str, dict] = {}
        for tool, stats in by_tool.items():
            entry: dict = {"count": stats["count"]}
            if stats["has_duration"] and stats["count"] > 0:
                entry["avg_duration_ms"] = round(
                    stats["total_duration_ms"] / stats["count"]
                )
            by_tool_clean[tool] = entry

        return {
            "date": date_str,
            "total_events": len(events),
            "by_tool": by_tool_clean,
        }

    def get_weekly_summary(self) -> dict:
        """Get summary for the last 7 days with trend comparison.

        Returns:
            Summary dict with current week totals, daily breakdown,
            and comparison against the previous week (days 8-14).
        """
        today = date.today()

        # Current week: last 7 days (today inclusive)
        current_days = [(today - timedelta(days=i)).isoformat() for i in range(7)]
        current_summaries = [self.get_daily_summary(d) for d in current_days]
        current_total = sum(s["total_events"] for s in current_summaries)

        # Previous week: days 8-14
        previous_days = [(today - timedelta(days=i)).isoformat() for i in range(7, 14)]
        previous_summaries = [self.get_daily_summary(d) for d in previous_days]
        previous_total = sum(s["total_events"] for s in previous_summaries)

        # Trend calculation
        if previous_total > 0:
            trend_pct = round(
                ((current_total - previous_total) / previous_total) * 100, 1
            )
        else:
            trend_pct = None  # No previous data for comparison

        # Aggregate by tool across current week
        by_tool: dict[str, int] = {}
        for summary in current_summaries:
            for tool, stats in summary.get("by_tool", {}).items():
                by_tool[tool] = by_tool.get(tool, 0) + stats["count"]

        return {
            "period": f"{current_days[-1]} to {current_days[0]}",
            "total_events": current_total,
            "by_tool": by_tool,
            "daily": [
                {"date": s["date"], "events": s["total_events"]}
                for s in current_summaries
            ],
            "trend": {
                "previous_week_total": previous_total,
                "current_week_total": current_total,
                "change_pct": trend_pct,
            },
        }

    def get_pattern_usage(self) -> dict:
        """Get usage statistics mapped to CQE Patterns.

        Returns:
            Dict mapping pattern names to usage counts, computed from
            all events in the last 30 days.
        """
        today = date.today()
        pattern_counts: dict[str, int] = {}

        for i in range(30):
            day_str = (today - timedelta(days=i)).isoformat()
            events = self._load_events(day_str)
            for event in events:
                tool = event.get("tool", "")
                # Match tool name against pattern keywords
                for keyword, pattern in TOOL_PATTERN_MAP.items():
                    if keyword in tool:
                        pattern_counts[pattern] = (
                            pattern_counts.get(pattern, 0) + 1
                        )
                        break

        return {
            "period": f"Last 30 days (since {(today - timedelta(days=29)).isoformat()})",
            "patterns": pattern_counts,
            "total_mapped_events": sum(pattern_counts.values()),
        }

    def purge_old_events(self, retention_days: int = 90) -> int:
        """Delete event files older than retention_days.

        Args:
            retention_days: Number of days to retain. Files older than
                this are deleted.

        Returns:
            Number of files deleted.
        """
        cutoff = date.today() - timedelta(days=retention_days)
        deleted = 0

        for file_path in self._events_dir().iterdir():
            if not file_path.name.endswith(".jsonl"):
                continue
            # Parse date from filename (YYYY-MM-DD.jsonl)
            date_part = file_path.stem
            try:
                file_date = date.fromisoformat(date_part)
            except ValueError:
                continue
            if file_date < cutoff:
                try:
                    os.remove(file_path)
                    deleted += 1
                except OSError:
                    continue

        return deleted
