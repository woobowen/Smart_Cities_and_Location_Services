"""Single editable specification for report prose and original UI windows."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
_spec = json.loads((ROOT / "content/evidence_units.json").read_text(encoding="utf-8"))
UNITS = _spec["units"]
EXPECTED_WIDTH = _spec["expected_width"]
