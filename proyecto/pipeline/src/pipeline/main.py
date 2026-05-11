import typer

from pipeline import db
from pipeline.config import DB_PATH
from pipeline.steps import classify as classify_step
from pipeline.steps import clean as clean_step
from pipeline.steps import ingest as ingest_step
from pipeline.steps import llm_keywords as llm_keywords_step

app = typer.Typer(help="Excel -> SQLite pipeline (ingest -> clean -> llm-keywords -> classify).")


@app.command("init-db")
def init_db() -> None:
    """Create the SQLite database and tables."""
    db.init_schema()
    typer.echo(f"[init-db] schema applied at {DB_PATH}")


@app.command("ingest")
def ingest() -> None:
    """Load .xlsx files from data/raw/ into the raw_data table."""
    ingest_step.run()


@app.command("clean")
def clean() -> None:
    """Clean raw_data into cleaned_data."""
    clean_step.run()


@app.command("llm-keywords")
def llm_keywords() -> None:
    """Generate keywords with an LLM into keywords_data."""
    llm_keywords_step.run()


@app.command("classify")
def classify() -> None:
    """Predict categories with Random Forest into categorized_data."""
    classify_step.run()


@app.command("run")
def run_all() -> None:
    """Run all pipeline steps in order."""
    ingest_step.run()
    clean_step.run()
    llm_keywords_step.run()
    classify_step.run()


if __name__ == "__main__":
    app()
