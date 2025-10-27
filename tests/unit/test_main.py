"""
Testes unitários para o módulo principal (CLI) - versão limpa.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

from src.main import main


class TestMain:
    """Testes para a função main."""
    
    def test_main_basic_functionality(self):
        """Testa funcionalidade básica do main."""
        with patch('sys.argv', ['main.py', 'test.txt']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('src.main.ParserFactory.get_parser_for_path') as mock_get_parser, \
             patch('src.main.GTTSEngine') as mock_gtts_engine, \
             patch('pathlib.Path.mkdir'):
            
            # Configurar mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = "Texto de teste"
            mock_get_parser.return_value = mock_parser
            
            mock_engine = Mock()
            mock_engine.speak.return_value = Path("out/test.mp3")
            mock_gtts_engine.return_value = mock_engine
            
            # Executar
            main()
            
            # Verificar
            mock_parser.parse.assert_called_once()
            mock_engine.speak.assert_called_once()
    
    @patch('src.main.logger')
    def test_main_file_not_found(self, mock_logger):
        """Testa comportamento quando arquivo de entrada não existe."""
        with patch('sys.argv', ['main.py', 'nonexistent.txt']), \
             patch('pathlib.Path.exists', return_value=False):
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            mock_logger.error.assert_called()
    
    @patch('src.main.logger')
    def test_main_unsupported_file_type(self, mock_logger):
        """Testa tipo de arquivo não suportado."""
        with patch('sys.argv', ['main.py', 'file.pdf']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('src.main.ParserFactory.get_parser_for_path', side_effect=ValueError("Tipo não suportado")):
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            mock_logger.error.assert_called()
    
    @patch('src.main.logger')
    def test_main_empty_text(self, mock_logger):
        """Testa arquivo com texto vazio."""
        with patch('sys.argv', ['main.py', 'empty.txt']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('src.main.ParserFactory.get_parser_for_path') as mock_get_parser:
            
            mock_parser = Mock()
            mock_parser.parse.return_value = ""
            mock_get_parser.return_value = mock_parser
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            mock_logger.error.assert_called()
    
    def test_main_pyttsx3_engine(self):
        """Testa uso do engine pyttsx3."""
        with patch('sys.argv', ['main.py', 'test.txt', '--engine', 'pyttsx3']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('src.main.ParserFactory.get_parser_for_path') as mock_get_parser, \
             patch('src.main.Pyttsx3Engine') as mock_pyttsx3_engine, \
             patch('pathlib.Path.mkdir'):
            
            # Configurar mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = "Texto de teste"
            mock_get_parser.return_value = mock_parser
            
            mock_engine = Mock()
            mock_engine.speak.return_value = Path("out/test.wav")
            mock_pyttsx3_engine.return_value = mock_engine
            
            # Executar
            main()
            
            # Verificar
            mock_pyttsx3_engine.assert_called_once()
            mock_engine.speak.assert_called_once()
    
    def test_main_custom_output(self):
        """Testa saída customizada."""
        with patch('sys.argv', ['main.py', 'test.txt', '--output', 'custom.mp3']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('src.main.ParserFactory.get_parser_for_path') as mock_get_parser, \
             patch('src.main.GTTSEngine') as mock_gtts_engine:
            
            # Configurar mocks
            mock_parser = Mock()
            mock_parser.parse.return_value = "Texto de teste"
            mock_get_parser.return_value = mock_parser
            
            mock_engine = Mock()
            mock_engine.speak.return_value = Path("custom.mp3")
            mock_gtts_engine.return_value = mock_engine
            
            # Executar
            main()
            
            # Verificar que foi chamado com o caminho customizado
            call_args = mock_engine.speak.call_args
            assert call_args[0][1] == Path("custom.mp3")