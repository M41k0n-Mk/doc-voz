"""
Testes unitários para o módulo TTS.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

from src.tts.base import TTSEngine
from src.tts.gtts_engine import GTTSEngine
from src.tts.pyttsx3_engine import Pyttsx3Engine


class TestTTSEngineBase:
    """Testes para a classe base TTSEngine."""
    
    def test_tts_engine_is_abstract(self):
        """Testa que TTSEngine não pode ser instanciada diretamente."""
        with pytest.raises(TypeError):
            TTSEngine()
    
    def test_tts_engine_subclass_must_implement_speak(self):
        """Testa que subclasses devem implementar speak."""
        class IncompleteTTSEngine(TTSEngine):
            pass
        
        with pytest.raises(TypeError):
            IncompleteTTSEngine()


class TestGTTSEngine:
    """Testes para GTTSEngine."""
    
    def test_init_default_values(self):
        """Testa inicialização com valores padrão."""
        engine = GTTSEngine()
        assert engine.MAX_CHUNK_SIZE == 5000
        assert engine.lang == "pt"
        assert engine.slow == False
    
    @patch('src.tts.gtts_engine.gTTS')
    def test_speak_small_text(self, mock_gtts):
        """Testa geração de áudio para texto pequeno."""
        # Arrange
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        engine = GTTSEngine()
        text = "Texto pequeno"
        output_path = Path("/tmp/test.mp3")
        
        # Act
        result = engine.speak(text, output_path)
        
        # Assert
        mock_gtts.assert_called_once_with(text, lang="pt", slow=False)
        mock_tts_instance.save.assert_called_once_with(str(output_path))
        assert result == output_path
    
    @patch('src.tts.gtts_engine.AudioSegment')
    @patch('src.tts.gtts_engine.gTTS')
    def test_speak_large_text_with_pydub(self, mock_gtts, mock_audio_segment):
        """Testa geração de áudio para texto grande com pydub disponível."""
        # Arrange
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        mock_audio_segment.empty.return_value = Mock()
        mock_audio_segment.from_mp3.return_value = Mock()
        mock_audio_segment.silent.return_value = Mock()
        
        engine = GTTSEngine()
        large_text = "A " * 3000  # 6000 caracteres
        output_path = Path("/tmp/test_large.mp3")
        
        with patch.object(engine, '_combine_audio_files') as mock_combine:
            # Act
            result = engine.speak(large_text, output_path)
            
            # Assert
            assert result == output_path
            mock_combine.assert_called_once()
            assert mock_gtts.call_count > 1  # Múltiplas chamadas para chunks
    
    def test_split_text_intelligently_small_text(self):
        """Testa divisão de texto pequeno."""
        engine = GTTSEngine()
        text = "Texto pequeno"
        
        chunks = engine._split_text_intelligently(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_split_text_intelligently_large_text(self):
        """Testa divisão de texto grande."""
        engine = GTTSEngine()
        text = "A " * 3000  # 6000 caracteres
        
        chunks = engine._split_text_intelligently(text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= engine.MAX_CHUNK_SIZE for chunk in chunks)
        assert "".join(chunks).replace(" ", "").strip() == text.replace(" ", "").strip()
    
    def test_find_best_split_point_paragraph(self):
        """Testa encontrar ponto de quebra em parágrafo."""
        engine = GTTSEngine()
        text = "Primeiro parágrafo.\n\nSegundo parágrafo."
        
        split_point = engine._find_best_split_point(text)
        
        assert split_point > 0
        assert text[split_point-2:split_point] == "\n\n"
    
    def test_find_best_split_point_sentence(self):
        """Testa encontrar ponto de quebra em sentença."""
        engine = GTTSEngine()
        text = "Primeira sentença. Segunda sentença."
        
        split_point = engine._find_best_split_point(text)
        
        assert split_point > 0
        assert text[split_point-2:split_point] == ". "
    
    def test_find_best_split_point_comma(self):
        """Testa encontrar ponto de quebra em vírgula."""
        engine = GTTSEngine()
        text = "Primeira parte, segunda parte"
        
        split_point = engine._find_best_split_point(text)
        
        assert split_point > 0
        assert text[split_point-2:split_point] == ", "
    
    def test_find_best_split_point_no_punctuation(self):
        """Testa quando não há pontuação adequada."""
        engine = GTTSEngine()
        text = "palavra " * 1000  # Só palavras e espaços
        chunk = text[:engine.MAX_CHUNK_SIZE]  # Pega só os primeiros 5000 caracteres
        
        split_point = engine._find_best_split_point(chunk)
        
        # Deve retornar -1 (não encontrou ponto adequado) ou 
        # o final do chunk se não há pontuação
        assert split_point == -1 or split_point == len(chunk)
    
    @patch('src.tts.gtts_engine.AudioSegment')
    @patch('src.tts.gtts_engine.os.path.exists')
    @patch('src.tts.gtts_engine.os.path.getsize')
    def test_combine_audio_files(self, mock_getsize, mock_exists, mock_audio_segment):
        """Testa combinação de arquivos de áudio."""
        # Arrange
        mock_exists.return_value = True
        mock_getsize.return_value = 1000  # Arquivo não vazio
        
        # Configurar mocks para permitir += nas operações
        mock_combined = Mock()
        mock_audio_segment.empty.return_value = mock_combined
        
        # Mock para permitir a operação combined += audio
        mock_audio = Mock()
        mock_audio_segment.from_mp3.return_value = mock_audio
        mock_combined.__iadd__ = Mock(return_value=mock_combined)
        
        mock_audio_segment.silent.return_value = Mock()
        
        engine = GTTSEngine()
        temp_files = ["/tmp/chunk1.mp3", "/tmp/chunk2.mp3"]
        output_path = Path("/tmp/combined.mp3")
        
        # Act
        engine._combine_audio_files(temp_files, output_path)
        
        # Assert
        assert mock_audio_segment.from_mp3.call_count == 2
        # Verifica se += foi chamado (combine audio segments + silences)
        # 2 arquivos + 1 silêncio entre eles + silêncio final = 4 operações
        assert mock_combined.__iadd__.call_count == 4
        mock_combined.export.assert_called_once_with(str(output_path), format="mp3")
    
    @patch('src.tts.gtts_engine.gTTS')
    def test_speak_directory_creation(self, mock_gtts):
        """Testa criação de diretório de saída."""
        mock_tts_instance = Mock()
        mock_gtts.return_value = mock_tts_instance
        
        engine = GTTSEngine()
        text = "Texto teste"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "test.mp3"
            
            result = engine.speak(text, output_path)
            
            assert output_path.parent.exists()
            assert result == output_path


class TestPyttsx3Engine:
    """Testes para Pyttsx3Engine."""
    
    @patch('src.tts.pyttsx3_engine.pyttsx3.init')
    def test_speak_basic(self, mock_pyttsx3_init):
        """Testa geração básica de áudio com pyttsx3."""
        # Arrange
        mock_engine = Mock()
        mock_pyttsx3_init.return_value = mock_engine
        mock_engine.getProperty.return_value = []  # Lista vazia de vozes
        
        engine = Pyttsx3Engine()
        text = "Texto teste"
        output_path = Path("/tmp/test.wav")
        
        # Act
        result = engine.speak(text, output_path)
        
        # Assert
        mock_engine.setProperty.assert_any_call("rate", 150)
        mock_engine.save_to_file.assert_called_once_with(text, str(output_path))
        mock_engine.runAndWait.assert_called_once()
        assert result == output_path
    
    @patch('src.tts.pyttsx3_engine.pyttsx3.init')
    def test_speak_voice_selection(self, mock_pyttsx3_init):
        """Testa seleção de voz feminina."""
        # Arrange
        mock_engine = Mock()
        mock_pyttsx3_init.return_value = mock_engine
        
        # Mock de vozes disponíveis
        mock_voice_male = Mock()
        mock_voice_male.name = "Male Voice"
        mock_voice_male.id = "male_voice_id"
        
        mock_voice_female = Mock()
        mock_voice_female.name = "Female Voice"
        mock_voice_female.id = "female_voice_id"
        
        mock_engine.getProperty.return_value = [mock_voice_male, mock_voice_female]
        
        engine = Pyttsx3Engine()
        text = "Texto teste"
        output_path = Path("/tmp/test.wav")
        
        # Act
        result = engine.speak(text, output_path)
        
        # Assert
        # Deve ter tentado configurar a voz feminina
        calls = mock_engine.setProperty.call_args_list
        voice_calls = [call for call in calls if call[0][0] == "voice"]
        assert len(voice_calls) == 1
        assert voice_calls[0][0][1] == "female_voice_id"
    
    @patch('src.tts.pyttsx3_engine.pyttsx3.init')
    def test_speak_voice_selection_exception(self, mock_pyttsx3_init):
        """Testa tratamento de erro na seleção de voz."""
        # Arrange
        mock_engine = Mock()
        mock_pyttsx3_init.return_value = mock_engine
        mock_engine.getProperty.side_effect = Exception("Erro ao listar vozes")
        
        engine = Pyttsx3Engine()
        text = "Texto teste"
        output_path = Path("/tmp/test.wav")
        
        # Act - não deve gerar exceção
        result = engine.speak(text, output_path)
        
        # Assert
        mock_engine.save_to_file.assert_called_once_with(text, str(output_path))
        assert result == output_path
    
    @patch('src.tts.pyttsx3_engine.pyttsx3.init')
    def test_speak_directory_creation(self, mock_pyttsx3_init):
        """Testa criação de diretório de saída."""
        mock_engine = Mock()
        mock_pyttsx3_init.return_value = mock_engine
        mock_engine.getProperty.return_value = []
        
        engine = Pyttsx3Engine()
        text = "Texto teste"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "subdir" / "test.wav"
            
            result = engine.speak(text, output_path)
            
            assert output_path.parent.exists()
            assert result == output_path