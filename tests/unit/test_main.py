"""
Testes unitários para o módulo principal (CLI).
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
    
    def test_main_file_not_found(self):
        """Testa comportamento quando arquivo não existe."""
        with patch('sys.argv', ['main.py', 'nonexistent.txt']), \
             patch('pathlib.Path.exists', return_value=False):
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
    
    def test_main_unsupported_file_type(self):
        """Testa tipo de arquivo não suportado."""
        with patch('sys.argv', ['main.py', 'file.pdf']), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('src.main.ParserFactory.get_parser_for_path', side_effect=ValueError("Tipo não suportado")):
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
    
    def test_main_empty_text(self):
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
import pytest
import sys
import argparse
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

from src.main import main


class TestMain:
    """Testes para a função main."""
    
    @patch('src.main.get_logger')
    @patch('src.main.ParserFactory.get_parser_for_path')
    @patch('pathlib.Path.exists')
    def test_main_file_not_found(self, mock_exists, mock_get_parser, mock_get_logger):
        """Testa comportamento quando arquivo de entrada não existe."""
        # Arrange
        mock_exists.return_value = False
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        # Act
        with patch('sys.argv', ['main.py', 'nonexistent.txt']):
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Assert
        assert exc_info.value.code == 1
        mock_logger.error.assert_called()
        mock_get_parser.assert_not_called()
    
    @patch('src.main.setup_logger')
    @patch('src.main.ParserFactory.create_parser')
    @patch('src.main.Path.exists')
    def test_main_unsupported_file_type(self, mock_exists, mock_create_parser, mock_setup_logger):
        """Testa comportamento com tipo de arquivo não suportado."""
        # Arrange
        mock_exists.return_value = True
        mock_create_parser.return_value = None
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        # Act
        with patch('sys.argv', ['main.py', 'file.pdf', 'output.mp3']):
            result = main()
        
        # Assert
        assert result == 1
        mock_logger.error.assert_called_with("Tipo de arquivo não suportado: .pdf")
    
    @patch('src.main.setup_logger')
    @patch('src.main.ParserFactory.create_parser')
    @patch('src.main.GTTSEngine')
    @patch('src.main.Path.exists')
    def test_main_gtts_engine_success(self, mock_exists, mock_gtts_engine, mock_create_parser, mock_setup_logger):
        """Testa execução bem-sucedida com engine gTTS."""
        # Arrange
        mock_exists.return_value = True
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_parser = Mock()
        mock_parser.parse.return_value = "Texto do arquivo"
        mock_create_parser.return_value = mock_parser
        
        mock_engine_instance = Mock()
        mock_engine_instance.speak.return_value = Path("output.mp3")
        mock_gtts_engine.return_value = mock_engine_instance
        
        # Act
        with patch('sys.argv', ['main.py', 'input.txt', 'output.mp3']):
            result = main()
        
        # Assert
        assert result == 0
        mock_parser.parse.assert_called_once_with(Path("input.txt"))
        mock_engine_instance.speak.assert_called_once_with("Texto do arquivo", Path("output.mp3"))
        mock_logger.info.assert_any_call("Processando arquivo: input.txt")
        mock_logger.info.assert_any_call("Áudio salvo em: output.mp3")
    
    @patch('src.main.setup_logger')
    @patch('src.main.ParserFactory.create_parser')
    @patch('src.main.Pyttsx3Engine')
    @patch('src.main.Path.exists')
    def test_main_pyttsx3_engine_success(self, mock_exists, mock_pyttsx3_engine, mock_create_parser, mock_setup_logger):
        """Testa execução bem-sucedida com engine Pyttsx3."""
        # Arrange
        mock_exists.return_value = True
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_parser = Mock()
        mock_parser.parse.return_value = "Texto do arquivo"
        mock_create_parser.return_value = mock_parser
        
        mock_engine_instance = Mock()
        mock_engine_instance.speak.return_value = Path("output.wav")
        mock_pyttsx3_engine.return_value = mock_engine_instance
        
        # Act
        with patch('sys.argv', ['main.py', 'input.txt', 'output.wav', '--engine', 'pyttsx3']):
            result = main()
        
        # Assert
        assert result == 0
        mock_pyttsx3_engine.assert_called_once()
        mock_engine_instance.speak.assert_called_once_with("Texto do arquivo", Path("output.wav"))
    
    @patch('src.main.setup_logger')
    @patch('src.main.ParserFactory.create_parser')
    @patch('src.main.GTTSEngine')
    @patch('src.main.Path.exists')
    def test_main_parsing_error(self, mock_exists, mock_gtts_engine, mock_create_parser, mock_setup_logger):
        """Testa tratamento de erro durante parsing."""
        # Arrange
        mock_exists.return_value = True
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_parser = Mock()
        mock_parser.parse.side_effect = Exception("Erro de parsing")
        mock_create_parser.return_value = mock_parser
        
        # Act
        with patch('sys.argv', ['main.py', 'input.txt', 'output.mp3']):
            result = main()
        
        # Assert
        assert result == 1
        mock_logger.error.assert_called_with("Erro ao processar arquivo: Erro de parsing")
    
    @patch('src.main.setup_logger')
    @patch('src.main.ParserFactory.create_parser')
    @patch('src.main.GTTSEngine')
    @patch('src.main.Path.exists')
    def test_main_tts_error(self, mock_exists, mock_gtts_engine, mock_create_parser, mock_setup_logger):
        """Testa tratamento de erro durante conversão TTS."""
        # Arrange
        mock_exists.return_value = True
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_parser = Mock()
        mock_parser.parse.return_value = "Texto do arquivo"
        mock_create_parser.return_value = mock_parser
        
        mock_engine_instance = Mock()
        mock_engine_instance.speak.side_effect = Exception("Erro TTS")
        mock_gtts_engine.return_value = mock_engine_instance
        
        # Act
        with patch('sys.argv', ['main.py', 'input.txt', 'output.mp3']):
            result = main()
        
        # Assert
        assert result == 1
        mock_logger.error.assert_called_with("Erro ao processar arquivo: Erro TTS")
    
    @patch('src.main.setup_logger')
    @patch('src.main.ParserFactory.create_parser')
    @patch('src.main.GTTSEngine')
    @patch('src.main.Path.exists')
    def test_main_verbose_logging(self, mock_exists, mock_gtts_engine, mock_create_parser, mock_setup_logger):
        """Testa configuração de logging verbose."""
        # Arrange
        mock_exists.return_value = True  
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        mock_parser = Mock()  
        mock_parser.parse.return_value = "Texto do arquivo"
        mock_create_parser.return_value = mock_parser
        
        mock_engine_instance = Mock()
        mock_engine_instance.speak.return_value = Path("output.mp3")
        mock_gtts_engine.return_value = mock_engine_instance
        
        # Act
        with patch('sys.argv', ['main.py', 'input.txt', 'output.mp3', '--verbose']):
            result = main()
        
        # Assert
        # Verifica se logger foi configurado com nível DEBUG
        mock_setup_logger.assert_called_with("doc_voz", level=pytest.approx(10))  # DEBUG = 10
        assert result == 0
    
    @patch('src.main.setup_logger')
    def test_main_argument_parsing_error(self, mock_setup_logger):
        """Testa tratamento de erro no parsing de argumentos."""
        mock_logger = Mock()
        mock_setup_logger.return_value = mock_logger
        
        # Act - argumentos inválidos
        with patch('sys.argv', ['main.py']):  # Faltam argumentos obrigatórios
            result = main()
        
        # Assert
        assert result == 1
        mock_logger.error.assert_called()
    
    def test_main_integration_docx_file(self):
        """Testa integração com arquivo DOCX."""
        with patch('src.main.setup_logger') as mock_setup_logger, \
             patch('src.main.ParserFactory.create_parser') as mock_create_parser, \
             patch('src.main.GTTSEngine') as mock_gtts_engine, \
             patch('src.main.Path.exists') as mock_exists:
            
            # Arrange
            mock_exists.return_value = True
            mock_logger = Mock()
            mock_setup_logger.return_value = mock_logger
            
            mock_parser = Mock()
            mock_parser.parse.return_value = "Conteúdo do DOCX"
            mock_create_parser.return_value = mock_parser
            
            mock_engine_instance = Mock()
            mock_engine_instance.speak.return_value = Path("output.mp3")
            mock_gtts_engine.return_value = mock_engine_instance
            
            # Act
            with patch('sys.argv', ['main.py', 'document.docx', 'output.mp3']):
                result = main()
            
            # Assert
            assert result == 0
            mock_create_parser.assert_called_once_with(".docx")
            mock_parser.parse.assert_called_once_with(Path("document.docx"))
    
    def test_main_empty_file_content(self):
        """Testa comportamento com arquivo vazio."""
        with patch('src.main.setup_logger') as mock_setup_logger, \
             patch('src.main.ParserFactory.create_parser') as mock_create_parser, \
             patch('src.main.GTTSEngine') as mock_gtts_engine, \
             patch('src.main.Path.exists') as mock_exists:
            
            # Arrange
            mock_exists.return_value = True
            mock_logger = Mock()
            mock_setup_logger.return_value = mock_logger
            
            mock_parser = Mock()
            mock_parser.parse.return_value = ""  # Arquivo vazio
            mock_create_parser.return_value = mock_parser
            
            mock_engine_instance = Mock()
            mock_engine_instance.speak.return_value = Path("output.mp3")
            mock_gtts_engine.return_value = mock_engine_instance
            
            # Act
            with patch('sys.argv', ['main.py', 'empty.txt', 'output.mp3']):
                result = main()
            
            # Assert
            assert result == 0
            mock_engine_instance.speak.assert_called_once_with("", Path("output.mp3"))