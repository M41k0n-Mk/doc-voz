from __future__ import annotations
from pathlib import Path
from .base import TTSEngine
import pyttsx3
from ..utils.logger import get_logger

logger = get_logger("pyttsx3")


class Pyttsx3Engine(TTSEngine):
    """Engine TTS offline usando pyttsx3.

    Gera arquivos WAV localmente (dependendo da plataforma).
    """

    def speak(self, text: str, out_path: Path) -> Path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        engine = pyttsx3.init()
        # Velocidade padrão
        engine.setProperty("rate", 150)
        # Tenta escolher voz feminina se disponível
        try:
            voices = engine.getProperty("voices")
            for v in voices:
                name_l = (v.name or "").lower()
                id_l = (v.id or "").lower()
                if "female" in name_l or "female" in id_l or "frau" in name_l or "mulher" in name_l:
                    engine.setProperty("voice", v.id)
                    break
        except Exception:
            # se não for possível listar/selecionar vozes, segue com a padrão
            logger.debug("Não foi possível selecionar voz específica")

        # pyttsx3 geralmente gera WAV; vamos confiar na extensão fornecida pelo usuário
        engine.save_to_file(text, str(out_path))
        engine.runAndWait()
        logger.info(f"Áudio salvo em: {out_path}")
        return out_path
