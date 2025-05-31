import sys
from pathlib import Path

# Find the project root (where pyproject.toml is)
repo_root = Path(__file__).resolve().parent.parent.parent.parent
pyproject = repo_root / "pyproject.toml"
if pyproject.exists():
    src_path = repo_root / "src"
    sys.path.insert(0, str(src_path))

