# Interactive Dungeon Master Project

This repository contains narrative exports in HTML format used to track lore, events, and characters for a role-playing campaign.

The project aims to build a digital interface where an AI acts as the Dungeon Master (DM). The AI can consult and update a database containing game rules, world lore, character sheets, and event history. Players will interact through a simple command-line interface in this prototype.

## Contents

- `eventos/`, `hilo_narrativo/`, `hojas_de_personaje/`, `tecnicas_liang/` – HTML exports with campaign information.
- `src/` – Source code for the interactive DM prototype.

## Usage

```
python3 -m dm.cli
```

This will start a basic command-line session where you can type actions or questions. The DM uses a small JSON database (`game_state.json`) to track the world state.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Example Character JSON

The world state is stored in `game_state.json`. Each entry under `characters` is a complete sheet represented as JSON. Below is the structure used for **Liáng Wǔzhào**:

```json
{
  "name": "Liáng Wǔzhào",
  "level": 5,
  "class": "Monk (Custom Subclass: Dao Geométrico)",
  "race": "Human",
  "alignment": "Lawful Neutral",
  "background": "Hermit",
  "experience": 29600,
  "attributes": {
    "strength": 10,
    "dexterity": 16,
    "constitution": 12,
    "intelligence": 20,
    "wisdom": 16,
    "charisma": 10
  },
  "proficiency_bonus": 3,
  "saving_throws": {
    "strength": false,
    "dexterity": true,
    "constitution": false,
    "intelligence": true,
    "wisdom": true,
    "charisma": false
  },
  "skills": {
    "arcana": true,
    "insight": true,
    "perception": true,
    "acrobatics": true,
    "history": true
  },
  "hit_points": {
    "max": 40,
    "current": 40
  },
  "armor_class": 14,
  "speed": 30,
  "languages": ["Common", "Celestial", "Primordial"],
  "features_traits": [
    {
      "name": "Micronúcleo",
      "description": "Contenedor comprimido de chi que almacena 132 puntos de maná condensado para respuestas rápidas o técnicas instantáneas."
    }
    // ...more traits...
  ],
  "resources": {
    "mana": {"max": 4730, "current": 4730},
    "micronucleo": 132
  },
  "custom_properties": {
    "dao": "Razonado",
    "afiliacion": "Secta de la Llama Partida (Cuatro Estandartes)",
    "estado": "En Reclusión Estructural Completa",
    "reclusion": {"inicio_dia": 115, "fin_dia": 470, "dias_restantes": 355},
    "titulos": {
      "activos": ["Portador del Silencio del Diseño Absoluto"],
      "retirados": ["El que Rediseñó su Reflejo", "El que Cortó la Escritura", "Variable Estable"]
    },
    "elementos_compatibles": [
      "Fuego – Presión térmica",
      "Físico – Biomecánica",
      "Aire – Evasión",
      "Agua – Recuperación",
      "Luz – Precisión",
      "Vacío – Reacción anti-signatura"
    ]
  }
}
```

This format can be extended for additional characters and stored directly in the `characters` field of the database file.
