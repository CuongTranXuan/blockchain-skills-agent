from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AgentLogger:
    """Structured execution logger producing agent_log.json (Protocol Labs format)."""

    def __init__(self, erc8004_address: str, output_path: str = "agent_log.json"):
        self._session = str(uuid.uuid4())
        self._erc8004 = erc8004_address
        self._started = datetime.now(timezone.utc).isoformat()
        self._entries: list[dict[str, Any]] = []
        self._path = Path(output_path)
        self._counter = 0

    def entry(
        self,
        phase: str,
        action: str,
        skill: str,
        input_data: Any = None,
        output_data: Any = None,
        status: str = "success",
        error: str | None = None,
    ) -> dict[str, Any]:
        self._counter += 1
        rec: dict[str, Any] = {
            "id": self._counter,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "action": action,
            "skill": skill,
            "input": _safe(input_data),
            "output": _safe(output_data),
            "status": status,
        }
        if error:
            rec["error"] = error
        self._entries.append(rec)
        self._flush()
        return rec

    def finalize(self) -> dict[str, Any]:
        doc = {
            "agent": "blockchain-skills-agent",
            "session": self._session,
            "erc8004": self._erc8004,
            "startedAt": self._started,
            "finishedAt": datetime.now(timezone.utc).isoformat(),
            "entries": self._entries,
        }
        self._path.write_text(json.dumps(doc, indent=2))
        return doc

    def _flush(self) -> None:
        """Write current state to disk after every entry (crash-safe)."""
        doc = {
            "agent": "blockchain-skills-agent",
            "session": self._session,
            "erc8004": self._erc8004,
            "startedAt": self._started,
            "entries": self._entries,
        }
        self._path.write_text(json.dumps(doc, indent=2))


def _safe(obj: Any) -> Any:
    """Convert dataclass/object to dict if it has to_dict, else return as-is."""
    if obj is None:
        return {}
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    return obj
