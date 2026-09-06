"""Shared pytest configuration for the `soulstruct-havok` test suite.

Ensures the local `src` package directory is importable without requiring an editable
install, so `pytest` can be run directly from the repository root.
"""
import sys
from pathlib import Path

_SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
