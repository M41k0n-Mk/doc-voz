#!/usr/bin/env python3
"""
Entrypoint CLI para o conversor de arquivos em áudio.
"""
from __future__ import annotations
import argparse
from pathlib import Path

from .utils.logger import get_logger
from .parsers.factory import ParserFactory
from .tts.gtts_engine import GTTSEngine
from .tts.pyttsx3_engine import Pyttsx3Engine

logger = get_logger("voice-reader")


def main() -> None:
    parser = argparse.ArgumentParser(description="Converte arquivo em áudio (txt, docx)")
    parser.add_argument("input", type=str, help="Caminho para o arquivo (.txt, .docx)")
    parser.add_argument("--engine", choices=["gtts", "pyttsx3"], default="gtts",
                        help="Engine TTS a usar (gtts grátis / pyttsx3 offline)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Caminho do arquivo de saída")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Arquivo não encontrado: {input_path}")
        raise SystemExit(1)

    try:
        parser_impl = ParserFactory.get_parser_for_path(input_path)
    except ValueError as e:
        logger.error(str(e))
        raise SystemExit(1)

    text = parser_impl.parse(input_path)
    if not text or not text.strip():
        logger.error("Nenhum texto extraído do arquivo.")
        raise SystemExit(1)

    # Saída padrão
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    if args.output:
        out_path = Path(args.output)
    else:
        ext = ".mp3" if args.engine == "gtts" else ".wav"
        out_path = out_dir / (input_path.stem + ext)

    engine = GTTSEngine() if args.engine == "gtts" else Pyttsx3Engine()
    saved = engine.speak(text, out_path)
    logger.info(f"Áudio gerado: {saved}")


if __name__ == "__main__":
    main()
