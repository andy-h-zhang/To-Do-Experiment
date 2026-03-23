"""Local dev: run from repo root as `backend/.venv/bin/python backend/app.py` or `cd backend && python app.py`."""

import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from api.index import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
