from __future__ import annotations
from abc import ABC, abstractmethod
from pathlib import Path


class TTSEngine(ABC):
    """Interface para engines de síntese de voz."""

    @abstractmethod
    def speak(self, text: str, out_path: Path) -> Path:
        """Gera o arquivo de áudio a partir do texto e retorna o caminho do arquivo gerado."""
        raise NotImplementedError()
