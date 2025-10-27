from __future__ import annotations
from pathlib import Path
from .base import Parser
from docx import Document


class DocxParser(Parser):
    """Parser para arquivos .docx usando python-docx"""

    def parse(self, path: Path) -> str:
        doc = Document(path)
        parts: list[str] = []
        for p in doc.paragraphs:
            if p.text:
                parts.append(p.text)
        return "\n".join(parts)
