"""Model code suggestions from a product title. Suggestions only: a person confirms the code."""

from __future__ import annotations

import re

TOKEN = re.compile(r"[A-Za-z0-9-]{6,}")


def model_code_candidates(title: str) -> list[str]:
    """Title words that mix letters and digits, e.g. "WGA25203TR" in "Bosch WGA25203TR 10 kg"."""
    return [t for t in TOKEN.findall(title)
            if any(c.isdigit() for c in t) and any(c.isalpha() for c in t)]
