from __future__ import annotations

from datetime import datetime

from .database import Database


class DungeonMaster:
    """Very simple Dungeon Master that logs events."""

    def __init__(self, db: Database):
        self.db = db

    def handle_input(self, player: str, text: str) -> str:
        """Process player input and return a DM response."""
        entry = f"{datetime.utcnow().isoformat()} - {player}: {text}"
        self.db.log_event(entry)

        lower = text.lower().strip()
        if lower == "mostrar reglas":
            import json
            return json.dumps(self.db.get_dm_rules(), ensure_ascii=False, indent=2)
        if lower == "mostrar mundo":
            import json
            return json.dumps(self.db.get_world_rules(), ensure_ascii=False, indent=2)
        if lower == "mostrar eventos":
            import json
            return json.dumps(self.db.get_narrative_events(), ensure_ascii=False, indent=2)

        return (
            f"{player}, has dicho: '{text}'.\n"
            f"(El DM registra el evento y continúa la aventura)."
        )
