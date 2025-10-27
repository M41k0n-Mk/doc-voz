from __future__ import annotations
from pathlib import Path
from .base import Parser


class TxtParser(Parser):
    """Parser simples para arquivos .txt"""

    def parse(self, path: Path) -> str:
        with path.open("r", encoding="utf-8") as fh:
            return fh.read()
