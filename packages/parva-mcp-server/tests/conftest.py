from __future__ import annotations

import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Iterator

import pytest

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture
def parva_http_stub() -> Iterator[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("content-length", "0"))
            request = json.loads(self.rfile.read(length).decode("utf-8"))
            calls.append({"path": self.path, "request": request})
            tool_name = request.get("tool_name")
            tool_input = request.get("input") or {}

            if tool_input.get("ad_date") == "9999-01-01":
                self._send(
                    400,
                    {
                        "detail": {
                            "code": "UNSUPPORTED_DATE_RANGE",
                            "message": "The supplied date is outside the supported range.",
                        }
                    },
                )
                return

            if tool_name == "parva.convert_date":
                result = {
                    "gregorian": tool_input.get("ad_date", "2026-04-14"),
                    "bikram_sambat": {
                        "year": 2083,
                        "month": 1,
                        "day": 1,
                        "month_name": "Baishakh",
                    },
                }
            elif tool_name == "parva.get_benchmark_summary":
                result = {
                    "task_count": 64,
                    "parva_score_percent": 86.09,
                    "static_score_percent": 19.38,
                    "claim_boundary": "technical_benchmark_not_authority",
                }
            else:
                result = {"received_tool": tool_name, "received_input": tool_input}

            self._send(
                200,
                {
                    "tool_name": tool_name,
                    "result": result,
                    "decision": {
                        "status": "approved",
                        "requires_human_review": False,
                        "reason_codes": ["TOOL_EXECUTED"],
                    },
                    "evidence": {"fact_ids": [], "source_ids": []},
                    "meta": {
                        "claim_boundary": "agent_temporal_reasoning_not_legal_authority",
                        "confidence": "source_backed",
                    },
                },
            )

        def _send(self, status: int, payload: dict[str, Any]) -> None:
            encoded = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: Any) -> None:
            del format, args

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield {
            "origin": f"http://127.0.0.1:{server.server_port}",
            "calls": calls,
        }
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
