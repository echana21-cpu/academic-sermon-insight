"""Module entry point for ``python -m sermon_insight``."""

from __future__ import annotations

import sys

from sermon_insight.cli import main

if __name__ == "__main__":
    sys.exit(main())
