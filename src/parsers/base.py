from __future__ import annotations
from pathlib import Path
from abc import ABC, abstractmethod


class Parser(ABC):
    """Interface para parsers de arquivos que retornam texto puro."""

    @abstractmethod
    def parse(self, path: Path) -> str:
        """Extrai e retorna o texto do arquivo.

        Args:
            path: caminho para o arquivo a ser lido

        Returns:
            Texto extraído (str)
        """
        raise NotImplementedError()
