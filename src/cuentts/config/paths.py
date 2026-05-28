from pathlib import Path

def find_project_root(start_path: Path, marker_file: str = "pyproject.toml") -> Path:
    current = start_path.resolve()
    while not (current / marker_file).exists() and current != current.parent:
        current = current.parent
    return current

BASE_DIR = find_project_root(Path(__file__))

TEMP_DIR = BASE_DIR / "temp"
TEMP_AUDIO_DIR = TEMP_DIR / "audio"

for path in [
    TEMP_DIR,
    TEMP_AUDIO_DIR,
]:
    path.mkdir(parents=True, exist_ok=True)