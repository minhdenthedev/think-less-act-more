from pathlib import Path


DATA_FOLDER = Path.home() / ".tlam"
DATA_FOLDER.mkdir(exist_ok=True, parents=True)
DATABASE_PATH = DATA_FOLDER / "data.db"

DELETE_ICON = "❌"
APPROVE_ICON = "✅"
