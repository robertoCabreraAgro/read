# Interactive Dungeon Master Project

This repository contains narrative exports in HTML format used to track lore, events, and characters for a role-playing campaign.

The project aims to build a digital interface where an AI acts as the Dungeon Master (DM). The AI can consult and update a database containing game rules, world lore, character sheets, and event history. Players interact through a simple command-line interface in this prototype.

## Contents

- `eventos/`, `hilo_narrativo/`, `hojas_de_personaje/`, `tecnicas_liang/` – HTML exports with campaign information.
- `src/` – Source code for the interactive DM prototype.

## Usage

```
python3 -m dm.cli
```

This will start a basic command-line session where you can type actions or questions. The DM uses a small JSON database (`game_state.json`) to track the world state.

The DM also stores rule sets and narrative summaries in that file. While in the
CLI you can view them with the following special commands:

```
mostrar reglas   # muestra las reglas de la IA y del sistema
mostrar mundo    # imprime información de ambientación
mostrar eventos  # lista los eventos narrativos principales
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
