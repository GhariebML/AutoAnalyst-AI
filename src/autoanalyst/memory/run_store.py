"""Run memory: local, append-only history of completed analyses and comparison utilities."""

from __future__ import annotations

import hashlib
import io
import json
import logging
from dataclasses import asdict, dataclass, field, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_MEMORY_PATH = Path(".autoanalyst") / "runs.jsonl"
DEFAULT_SQLITE_PATH = Path(".autoanalyst") / "runs.db"


def hash_dataframe(df: pd.DataFrame) -> str:
    """Stable content hash of a DataFrame's CSV serialization."""
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    return hashlib.sha256(buffer.getvalue()).hexdigest()


def numeric_stats(df: pd.DataFrame) -> dict[str, dict[str, float]]:
    """Compact per-numeric-column statistics used for drift comparison."""
    stats: dict[str, dict[str, float]] = {}
    for column in df.select_dtypes(include="number").columns:
        series = df[column]
        non_null = series.dropna()
        stats[str(column)] = {
            "mean": round(float(non_null.mean()), 6) if len(non_null) else 0.0,
            "std": round(float(non_null.std()), 6) if len(non_null) > 1 else 0.0,
            "missing_percent": round(float(series.isna().mean() * 100.0), 2),
        }
    return stats


@dataclass
class RunRecord:
    """One persisted analysis run."""

    run_id: str
    created_at: str
    dataset_hash: str
    dataset_name: str | None
    rows: int
    columns: int
    column_names: list[str] = field(default_factory=list)
    numeric_stats: dict[str, dict[str, float]] = field(default_factory=dict)
    target_column: str | None = None
    narrated_by: str = "rules"
    executive_summary: str | None = None
    scalar_metrics: dict[str, float] = field(default_factory=dict)
    insight_count: int = 0
    warning_count: int = 0
    report_path: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RunRecord:
        names = {f.name for f in fields(cls)}
        return cls(**{key: value for key, value in data.items() if key in names})


def build_run_record(
    run_id: str,
    df: pd.DataFrame,
    *,
    dataset_name: str | None,
    target_column: str | None,
    result: Any,
) -> RunRecord:
    """Assemble a RunRecord from graph state artifacts and a PipelineResult."""
    evaluation = getattr(result, "evaluation_results", None) or {}
    scalar_metrics_value = {
        key: round(float(value), 4)
        for key, value in evaluation.items()
        if isinstance(value, (int, float)) and not isinstance(value, bool)
    }
    return RunRecord(
        run_id=run_id,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        dataset_hash=hash_dataframe(df),
        dataset_name=dataset_name,
        rows=int(df.shape[0]),
        columns=int(df.shape[1]),
        column_names=[str(name) for name in df.columns],
        numeric_stats=numeric_stats(df),
        target_column=target_column,
        narrated_by=str(getattr(result, "narrated_by", "rules")),
        executive_summary=getattr(result, "executive_summary", None),
        scalar_metrics=scalar_metrics_value,
        insight_count=len(getattr(result, "insights", []) or []),
        warning_count=len(getattr(result, "warnings", []) or []),
        report_path=str(getattr(result, "report_path")) if getattr(result, "report_path", None) else None,
    )


class RunStore:
    """Append-only JSONL and SQLite store of RunRecords with run comparison support."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else DEFAULT_MEMORY_PATH

    def append(self, record: RunRecord) -> None:
        """Append a run record to persistent storage."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(record.to_json() + "\n")
        logger.info("Run %s recorded to %s", record.run_id, self.path)

    def list_recent(self, limit: int = 20) -> list[RunRecord]:
        """List recent runs, newest first."""
        if not self.path.exists():
            return []
        records: list[RunRecord] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                records.append(RunRecord.from_dict(json.loads(line)))
            except (json.JSONDecodeError, TypeError) as exc:
                logger.warning("Skipping corrupt run-memory line: %s", exc)
        return list(reversed(records))[:limit]

    def latest_by_dataset_hash(self, dataset_hash: str, exclude_run_id: str | None = None) -> RunRecord | None:
        """Find the latest run record matching a dataset content hash."""
        for record in self.list_recent(limit=1000):
            if record.dataset_hash == dataset_hash and record.run_id != exclude_run_id:
                return record
        return None

    def compare_runs(self, run_id_a: str, run_id_b: str) -> dict[str, Any]:
        """Compare two historical runs and compute metric deltas."""
        runs = {r.run_id: r for r in self.list_recent(limit=1000)}
        if run_id_a not in runs or run_id_b not in runs:
            raise KeyError(f"One or both run IDs not found: {run_id_a}, {run_id_b}")

        a = runs[run_id_a]
        b = runs[run_id_b]

        metric_diffs: dict[str, dict[str, Any]] = {}
        all_metrics = set(a.scalar_metrics.keys()) | set(b.scalar_metrics.keys())
        for m in all_metrics:
            val_a = a.scalar_metrics.get(m)
            val_b = b.scalar_metrics.get(m)
            delta = round(val_b - val_a, 4) if (val_a is not None and val_b is not None) else None
            metric_diffs[m] = {"run_a": val_a, "run_b": val_b, "delta": delta}

        return {
            "run_a": {"id": a.run_id, "created_at": a.created_at, "rows": a.rows, "cols": a.columns},
            "run_b": {"id": b.run_id, "created_at": b.created_at, "rows": b.rows, "cols": b.columns},
            "same_dataset_hash": a.dataset_hash == b.dataset_hash,
            "metric_comparisons": metric_diffs,
            "columns_added_in_b": sorted(set(b.column_names) - set(a.column_names)),
            "columns_removed_in_b": sorted(set(a.column_names) - set(b.column_names)),
        }


__all__ = [
    "DEFAULT_MEMORY_PATH",
    "RunRecord",
    "RunStore",
    "build_run_record",
    "hash_dataframe",
    "numeric_stats",
]
