"""Infrastructure adapter for precomputed artifact loading."""

from __future__ import annotations

import json
import time
from datetime import date, datetime, timezone
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

from app.reliability.metrics import MetricsRegistry


class PrecomputedArtifactCorruptionError(RuntimeError):
    """Raised when a precomputed artifact exists but cannot be parsed safely."""


@lru_cache(maxsize=32)
def _load_json_blob_cached(path_str: str, mtime_ns: int) -> dict[str, Any]:
    del mtime_ns
    path = Path(path_str)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PrecomputedArtifactCorruptionError(
            f"Malformed precomputed artifact: {path.name}"
        ) from exc
    except OSError as exc:
        raise PrecomputedArtifactCorruptionError(
            f"Unreadable precomputed artifact: {path.name}"
        ) from exc


@dataclass
class FilePrecomputedArtifactStore:
    precompute_dir: Path
    metrics: MetricsRegistry

    def clear(self) -> None:
        _load_json_blob_cached.cache_clear()

    def _read_json(self, path: Path) -> Optional[dict[str, Any]]:
        if not path.exists():
            return None
        try:
            stat = path.stat()
        except OSError:
            return None
        return _load_json_blob_cached(str(path), stat.st_mtime_ns)

    def load_panchanga(self, target_date: date) -> Optional[dict[str, Any]]:
        year_file = self.precompute_dir / f"panchanga_{target_date.year}.json"
        payload = self._read_json(year_file)
        if not payload:
            self.metrics.record_cache_lookup("panchanga", False)
            return None
        row = payload.get("dates", {}).get(target_date.isoformat())
        self.metrics.record_cache_lookup("panchanga", row is not None)
        return row

    def load_festival_year(self, year: int) -> Optional[dict[str, Any]]:
        path = self.precompute_dir / f"festivals_{year}.json"
        payload = self._read_json(path)
        self.metrics.record_cache_lookup("festival_year", payload is not None)
        return payload

    def get_stats(self) -> dict[str, Any]:
        self.precompute_dir.mkdir(parents=True, exist_ok=True)
        files = sorted(self.precompute_dir.glob("*.json"))
        total_bytes = sum(f.stat().st_size for f in files)
        modified_times = [f.stat().st_mtime for f in files]
        now_ts = datetime.now(timezone.utc).timestamp()
        newest_modified = max(modified_times) if modified_times else None
        oldest_modified = min(modified_times) if modified_times else None
        panchanga_files = [f for f in files if f.name.startswith("panchanga_")]
        festival_files = [f for f in files if f.name.startswith("festivals_")]
        return {
            "directory": str(self.precompute_dir),
            "file_count": len(files),
            "total_bytes": total_bytes,
            "freshness": {
                "newest_modified": newest_modified,
                "oldest_modified": oldest_modified,
                "newest_age_seconds": round(now_ts - newest_modified, 3) if newest_modified else None,
                "oldest_age_seconds": round(now_ts - oldest_modified, 3) if oldest_modified else None,
            },
            "artifact_classes": {
                "panchanga": {
                    "file_count": len(panchanga_files),
                    "available": bool(panchanga_files),
                },
                "festivals": {
                    "file_count": len(festival_files),
                    "available": bool(festival_files),
                },
            },
            "files": [
                {
                    "name": f.name,
                    "size": f.stat().st_size,
                    "modified": f.stat().st_mtime,
                }
                for f in files
            ],
        }

    def prewarm_hot_set(self, today: Optional[date] = None) -> dict[str, Any]:
        target = today or date.today()
        warmed = {
            "target_date": target.isoformat(),
            "panchanga_today": self.load_panchanga(target) is not None,
            "festival_years": {},
        }
        for year in (target.year, target.year + 1):
            warmed["festival_years"][str(year)] = self.load_festival_year(year) is not None
        warmed["hit_count"] = int(warmed["panchanga_today"]) + sum(
            int(hit) for hit in warmed["festival_years"].values()
        )
        return warmed

    def measure_hotset_latency(self, today: Optional[date] = None) -> dict[str, Any]:
        target = today or date.today()
        self.clear()

        cold_started = time.perf_counter()
        cold_panchanga = self.load_panchanga(target) is not None
        cold_festival_current = self.load_festival_year(target.year) is not None
        cold_festival_next = self.load_festival_year(target.year + 1) is not None
        cold_ms = round((time.perf_counter() - cold_started) * 1000.0, 3)

        warm_started = time.perf_counter()
        warm_panchanga = self.load_panchanga(target) is not None
        warm_festival_current = self.load_festival_year(target.year) is not None
        warm_festival_next = self.load_festival_year(target.year + 1) is not None
        warm_ms = round((time.perf_counter() - warm_started) * 1000.0, 3)

        return {
            "target_date": target.isoformat(),
            "cold_ms": cold_ms,
            "warm_ms": warm_ms,
            "delta_ms": round(cold_ms - warm_ms, 3),
            "panchanga_hit": cold_panchanga and warm_panchanga,
            "festival_years": {
                str(target.year): cold_festival_current and warm_festival_current,
                str(target.year + 1): cold_festival_next and warm_festival_next,
            },
        }
