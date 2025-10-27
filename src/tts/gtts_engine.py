from __future__ import annotations
from pathlib import Path
from typing import List
import re
import tempfile
import os
from pydub import AudioSegment
from .base import TTSEngine
from gtts import gTTS
from ..utils.logger import get_logger

logger = get_logger("gtts")


class GTTSEngine(TTSEngine):
    """Engine TTS usando gTTS (Google Translate TTS) - solução grátis baseada na web.

    Suporta chunking automático para textos grandes (>5000 caracteres).
    Combina múltiplos chunks em um único arquivo de áudio final.
    """

    MAX_CHUNK_SIZE = 5000  # Limite de caracteres por chunk do gTTS
    
    def __init__(self):
        """Inicializa o engine com configurações padrão."""
        self.lang = "pt"
        self.slow = False

    def speak(self, text: str, out_path: Path) -> Path:
        """Gera áudio do texto, com chunking automático se necessário."""
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        
        text_length = len(text)
        logger.info(f"Processando texto com {text_length} caracteres")
        
        if text_length <= self.MAX_CHUNK_SIZE:
            # Texto pequeno - processamento direto
            return self._generate_single_audio(text, out_path)
        else:
            # Texto grande - usar chunking
            logger.info(f"Texto excede {self.MAX_CHUNK_SIZE} caracteres. Usando chunking...")
            return self._generate_chunked_audio(text, out_path)

    def _generate_single_audio(self, text: str, out_path: Path) -> Path:
        """Gera áudio para texto pequeno (método original)."""
        try:
            tts = gTTS(text, lang=self.lang, slow=self.slow)
            tts.save(str(out_path))
            logger.info(f"Áudio simples salvo em: {out_path}")
            return out_path
        except Exception as e:
            logger.error(f"Erro ao gerar áudio simples: {e}")
            raise

    def _generate_chunked_audio(self, text: str, out_path: Path) -> Path:
        """Gera áudio para texto grande usando chunking e concatenação."""
        chunks = self._split_text_intelligently(text)
        logger.info(f"Texto dividido em {len(chunks)} chunks")
        
        # Verificar se pydub está disponível
        try:
            import pydub
        except ImportError:
            logger.warning("pydub não está instalado. Usando fallback para chunk único...")
            # Fallback: pega apenas os primeiros MAX_CHUNK_SIZE caracteres
            truncated_text = text[:self.MAX_CHUNK_SIZE]
            logger.warning(f"Texto truncado para {len(truncated_text)} caracteres")
            return self._generate_single_audio(truncated_text, out_path)
        
        temp_files = []
        try:
            # Gerar áudio para cada chunk
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                    
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_chunk_{i}.mp3")
                temp_files.append(temp_file.name)
                temp_file.close()
                
                logger.info(f"Processando chunk {i+1}/{len(chunks)} ({len(chunk)} chars)")
                
                try:
                    tts = gTTS(chunk.strip(), lang=self.lang, slow=self.slow)
                    tts.save(temp_file.name)
                except Exception as e:
                    logger.error(f"Erro ao processar chunk {i+1}: {e}")
                    raise
            
            # Combinar todos os chunks em um único arquivo
            self._combine_audio_files(temp_files, out_path)
            logger.info(f"Áudio combinado salvo em: {out_path}")
            
            return out_path
            
        finally:
            # Limpar arquivos temporários
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"Erro ao limpar arquivo temporário {temp_file}: {e}")

    def _split_text_intelligently(self, text: str) -> List[str]:
        """Divide o texto em chunks inteligentemente, respeitando sentenças e parágrafos."""
        if len(text) <= self.MAX_CHUNK_SIZE:
            return [text]
        
        chunks = []
        remaining_text = text
        
        while remaining_text:
            if len(remaining_text) <= self.MAX_CHUNK_SIZE:
                chunks.append(remaining_text)
                break
            
            # Tentar encontrar um ponto de quebra natural
            chunk_end = self._find_best_split_point(remaining_text[:self.MAX_CHUNK_SIZE])
            
            if chunk_end == -1:
                # Se não encontrar ponto natural, força quebra no limite
                chunk_end = self.MAX_CHUNK_SIZE
            
            chunk = remaining_text[:chunk_end].strip()
            if chunk:
                chunks.append(chunk)
            
            remaining_text = remaining_text[chunk_end:].strip()
        
        return chunks

    def _find_best_split_point(self, text: str) -> int:
        """Encontra o melhor ponto para dividir o texto, priorizando pontos naturais."""
        # Prioridade 1: Final de parágrafo
        para_match = re.search(r'\n\s*\n', text)
        if para_match:
            return para_match.end()
        
        # Prioridade 2: Final de sentença (. ! ?)
        sentence_matches = list(re.finditer(r'[.!?]\s+', text))
        if sentence_matches:
            # Pega a última sentença que cabe no chunk
            return sentence_matches[-1].end()
        
        # Prioridade 3: Vírgula ou ponto e vírgula
        punct_matches = list(re.finditer(r'[,;]\s+', text))
        if punct_matches:
            return punct_matches[-1].end()
        
        # Prioridade 4: Espaço em branco
        space_match = text.rfind(' ')
        if space_match > len(text) * 0.8:  # Só se estiver nos últimos 20%
            return space_match + 1
        
        # Se não encontrar nada, retorna -1 para forçar quebra
        return -1

    def _combine_audio_files(self, temp_files: List[str], output_path: Path) -> None:
        """Combina múltiplos arquivos MP3 em um único arquivo."""
        try:
            combined = AudioSegment.empty()
            
            for temp_file in temp_files:
                if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                    audio = AudioSegment.from_mp3(temp_file)
                    combined += audio
                    # Adicionar pequena pausa entre chunks (300ms)
                    combined += AudioSegment.silent(duration=300)
            
            # Exportar arquivo final
            combined.export(str(output_path), format="mp3")
            
        except Exception as e:
            logger.error(f"Erro ao combinar arquivos de áudio: {e}")
            raise
