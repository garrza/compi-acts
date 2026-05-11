# Pipeline

Pipeline en Python para procesar un Excel de entrada, almacenarlo en una SQLite compartida, limpiarlo, generar keywords con un LLM local (Ollama) y clasificar con Random Forest.

## Setup

```bash
cd proyecto/pipeline
uv sync
```

## Uso

Los Excel de entrada van en `proyecto/data/raw/*.xlsx`. La SQLite compartida se crea en `proyecto/data/app.db`.

```bash
uv run pipeline init-db          # crea la DB y las tablas
uv run pipeline ingest           # carga los .xlsx a raw_data
uv run pipeline clean            # raw_data -> cleaned_data
uv run pipeline llm-keywords     # cleaned_data -> keywords_data
uv run pipeline classify         # keywords_data -> categorized_data
uv run pipeline run              # ejecuta todos los pasos en orden
```

## Estado

Scaffolding inicial. Cada paso es un stub; se implementarán uno por uno.
