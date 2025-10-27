from __future__ import annotations
from pathlib import Path
from .base import TTSEngine
from gtts import gTTS
from ..utils.logger import get_logger

logger = get_logger("gtts")


class GTTSEngine(TTSEngine):
    """Engine TTS usando gTTS (Google Translate TTS) - solução grátis baseada na web.

    Observação: gTTS realiza chamadas web para gerar o áudio.
    """

    def speak(self, text: str, out_path: Path) -> Path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # gTTS aceita strings; para textos muito grandes pode ser necessário chunking.
        tts = gTTS(text, lang="pt")
        tts.save(str(out_path))
        logger.info(f"Áudio salvo em: {out_path}")
        return out_path
