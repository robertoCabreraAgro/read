import json
from pathlib import Path
from typing import Any, Dict


class Database:
    """Simple JSON-based database for storing game state."""

    def __init__(self, path: Path):
        self.path = path
        if not self.path.exists():
            self._data: Dict[str, Any] = {
                "characters": {},
                "events": [],
                "dm_rules": {},
                "world_rules": {},
                "narrative_events": {}
            }
            self._save()
        else:
            self._load()

    def _load(self) -> None:
        with self.path.open("r", encoding="utf-8") as fh:
            self._data = json.load(fh)

    def _save(self) -> None:
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2, ensure_ascii=False)

    def get_character(self, name: str) -> Dict[str, Any]:
        return self._data["characters"].setdefault(name, {})

    def log_event(self, event: str) -> None:
        self._data["events"].append(event)
        self._save()

    def list_events(self) -> list:
        return list(self._data["events"])

    def get_dm_rules(self) -> Dict[str, Any]:
        """Return DM rules stored in the database."""
        return self._data.get("dm_rules", {})

    def get_world_rules(self) -> Dict[str, Any]:
        """Return world rules information."""
        return self._data.get("world_rules", {})

    def get_narrative_events(self) -> Dict[str, Any]:
        """Return narrative event summaries."""
        return self._data.get("narrative_events", {})
