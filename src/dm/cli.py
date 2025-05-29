import argparse
from pathlib import Path

from .database import Database
from .dungeon_master import DungeonMaster


def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive Dungeon Master")
    parser.add_argument("player", help="Name of the player")
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("game_state.json"),
        help="Path to database JSON file",
    )
    args = parser.parse_args()

    db = Database(args.db)
    dm = DungeonMaster(db)

    print("Bienvenido al sistema DM. Escribe 'salir' para terminar.")
    while True:
        try:
            text = input("\n> ")
        except EOFError:
            break
        if text.lower() in {"salir", "exit", "quit"}:
            break
        response = dm.handle_input(args.player, text)
        print(response)


if __name__ == "__main__":
    main()
