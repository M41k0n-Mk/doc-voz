from __future__ import annotations
from pathlib import Path
from typing import Type

from .base import Parser
from .txt_parser import TxtParser
from .docx_parser import DocxParser
from .code_parser import CodeParser


class ParserFactory:
    """Fábrica simples que escolhe um parser baseado na extensão do arquivo."""

    _map: dict[str, Type[Parser]] = {
        ".txt": TxtParser,
        ".docx": DocxParser,
        # Arquivos de código
        ".py": CodeParser,
        ".js": CodeParser,
        ".ts": CodeParser,
        ".java": CodeParser,
        ".cpp": CodeParser,
        ".c": CodeParser,
        ".cs": CodeParser,
        ".rb": CodeParser,
        ".go": CodeParser,
        ".php": CodeParser,
    }

    @classmethod
    def get_parser_for_path(cls, path: Path) -> Parser:
        ext = path.suffix.lower()
        parser_cls = cls._map.get(ext)
        if not parser_cls:
            raise ValueError(f"Extensão não suportada: {ext}")
        return parser_cls()
