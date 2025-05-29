# AI Dungeon Master CLI

Esta aplicación proporciona una interfaz de línea de comandos que utiliza una Inteligencia Artificial para dirigir partidas de rol y mantener la coherencia de un mundo persistente.

## Requisitos
- Python 3.10+
- Dependencias indicadas en `requirements.txt` (si existe)
- Una base de datos accesible vía SQLAlchemy (SQLite por defecto)
- Clave de API de OpenAI para las funciones de IA (opcional pero recomendada)

## Configuración
1. Copia `.env.example` a `.env` y ajusta los valores necesarios:
   ```
   DATABASE_URL="postgresql://usuario:password@localhost/tu_db"
   OPENAI_API_KEY="sk-tu_clave"
   ```
   Si `DATABASE_URL` no se define se usará `sqlite:///./default_dm_database.db`.

2. Instala las dependencias necesarias y ejecuta el script de población de datos:
   ```bash
   python populate_db.py
   ```

## Uso del CLI
Lanza el programa principal:
```bash
python main.py
```
Dentro del CLI escribe `help` para ver los comandos disponibles. Podrás añadir personajes, registrar eventos y conversar con el DM.

Los datos utilizados para poblar la base se encuentran en la carpeta `data/` en formato JSON para facilitar su modificación.

