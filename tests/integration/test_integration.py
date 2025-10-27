"""
Testes de integração para o doc-voz.
"""
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, Mock

from src.main import main
from src.parsers.factory import ParserFactory
from src.tts.gtts_engine import GTTSEngine
from src.tts.pyttsx3_engine import Pyttsx3Engine


class TestIntegration:
    """Testes de integração do sistema completo."""
    
    def test_end_to_end_txt_file_gtts(self):
        """Testa fluxo completo: TXT → Parser → gTTS → MP3."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar arquivo de entrada
            input_file = Path(temp_dir) / "test.txt"
            input_file.write_text("Este é um teste de integração do sistema doc-voz.")
            
            output_file = Path(temp_dir) / "output.mp3"
            
            # Mock do gTTS para não fazer chamadas reais
            with patch('src.tts.gtts_engine.gTTS') as mock_gtts:
                mock_tts_instance = Mock()
                mock_gtts.return_value = mock_tts_instance
                
                # Mock sys.argv
                with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                    result = main()
                
                # Verificações
                assert result == 0
                mock_gtts.assert_called_once_with(
                    "Este é um teste de integração do sistema doc-voz.",
                    lang="pt",
                    slow=False
                )
                mock_tts_instance.save.assert_called_once_with(str(output_file))
    
    def test_end_to_end_docx_file_pyttsx3(self):
        """Testa fluxo completo: DOCX → Parser → Pyttsx3 → WAV."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar arquivo DOCX de teste
            input_file = Path(temp_dir) / "test.docx"
            output_file = Path(temp_dir) / "output.wav"
            
            # Mock do python-docx
            with patch('src.parsers.docx_parser.Document') as mock_document:
                # Configurar mock para simular documento DOCX
                mock_doc = Mock()
                mock_paragraph = Mock()
                mock_paragraph.text = "Conteúdo do documento DOCX para teste."
                mock_doc.paragraphs = [mock_paragraph]
                mock_document.return_value = mock_doc
                
                # Mock do pyttsx3
                with patch('src.tts.pyttsx3_engine.pyttsx3.init') as mock_pyttsx3_init:
                    mock_engine = Mock()
                    mock_engine.getProperty.return_value = []
                    mock_pyttsx3_init.return_value = mock_engine
                    
                    # Simular existência do arquivo
                    with patch('pathlib.Path.exists', return_value=True):
                        # Mock sys.argv
                        with patch('sys.argv', [
                            'main.py', 
                            str(input_file), 
                            str(output_file), 
                            '--engine', 'pyttsx3'
                        ]):
                            result = main()
                    
                    # Verificações
                    assert result == 0
                    mock_document.assert_called_once_with(str(input_file))
                    mock_engine.save_to_file.assert_called_once_with(
                        "Conteúdo do documento DOCX para teste.",
                        str(output_file)
                    )
    
    def test_integration_large_text_chunking(self):
        """Testa integração com texto grande (chunking)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Criar texto grande (> 5000 caracteres)
            large_text = "Este é um parágrafo de teste. " * 200  # ~6000 caracteres
            
            input_file = Path(temp_dir) / "large.txt"
            input_file.write_text(large_text)
            
            output_file = Path(temp_dir) / "large_output.mp3"
            
            # Mock do gTTS e AudioSegment
            with patch('src.tts.gtts_engine.gTTS') as mock_gtts, \
                 patch('src.tts.gtts_engine.AudioSegment') as mock_audio_segment:
                
                mock_tts_instance = Mock()
                mock_gtts.return_value = mock_tts_instance
                
                # Mock do AudioSegment para chunking
                mock_combined = Mock()
                mock_audio_segment.empty.return_value = mock_combined
                mock_audio_segment.from_mp3.return_value = Mock()
                mock_audio_segment.silent.return_value = Mock()
                
                with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                    result = main()
                
                # Verificações
                assert result == 0
                # Deve ter feito múltiplas chamadas para gTTS (chunking)
                assert mock_gtts.call_count > 1
                # Deve ter tentado combinar os arquivos
                mock_combined.export.assert_called_once_with(str(output_file), format="mp3")
    
    def test_integration_parser_factory_selection(self):
        """Testa seleção automática de parser baseada na extensão."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Teste com diferentes extensões
            test_cases = [
                ("test.txt", "Conteúdo TXT"),
                ("test.docx", "Conteúdo DOCX")
            ]
            
            for filename, content in test_cases:
                input_file = Path(temp_dir) / filename
                output_file = Path(temp_dir) / f"output_{filename}.mp3"
                
                # Configurar mocks baseado no tipo de arquivo
                if filename.endswith('.txt'):
                    # Para TXT, apenas criar o arquivo
                    input_file.write_text(content)
                    
                    with patch('src.tts.gtts_engine.gTTS') as mock_gtts:
                        mock_tts_instance = Mock()
                        mock_gtts.return_value = mock_tts_instance
                        
                        with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                            result = main()
                        
                        assert result == 0
                        mock_gtts.assert_called_once_with(content, lang="pt", slow=False)
                
                elif filename.endswith('.docx'):
                    # Para DOCX, mockar Document
                    with patch('src.parsers.docx_parser.Document') as mock_document, \
                         patch('pathlib.Path.exists', return_value=True):
                        
                        mock_doc = Mock()
                        mock_paragraph = Mock()
                        mock_paragraph.text = content
                        mock_doc.paragraphs = [mock_paragraph]
                        mock_document.return_value = mock_doc
                        
                        with patch('src.tts.gtts_engine.gTTS') as mock_gtts:
                            mock_tts_instance = Mock()
                            mock_gtts.return_value = mock_tts_instance
                            
                            with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                                result = main()
                            
                            assert result == 0
                            mock_gtts.assert_called_once_with(content, lang="pt", slow=False)
    
    def test_integration_error_propagation(self):
        """Testa propagação de erros através do sistema."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "test.txt"
            input_file.write_text("Teste de erro")
            
            output_file = Path(temp_dir) / "output.mp3"
            
            # Simular erro no gTTS
            with patch('src.tts.gtts_engine.gTTS') as mock_gtts:
                mock_gtts.side_effect = Exception("Erro de rede no gTTS")
                
                with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                    result = main()
                
                # Deve retornar código de erro
                assert result == 1
    
    def test_integration_verbose_mode(self):
        """Testa modo verbose em integração completa."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "verbose_test.txt"
            input_file.write_text("Teste do modo verbose")
            
            output_file = Path(temp_dir) / "verbose_output.mp3"
            
            with patch('src.tts.gtts_engine.gTTS') as mock_gtts, \
                 patch('src.utils.logger.setup_logger') as mock_setup_logger:
                
                mock_tts_instance = Mock()
                mock_gtts.return_value = mock_tts_instance
                
                mock_logger = Mock()
                mock_setup_logger.return_value = mock_logger
                
                with patch('sys.argv', [
                    'main.py', 
                    str(input_file), 
                    str(output_file), 
                    '--verbose'
                ]):
                    result = main()
                
                # Verificações
                assert result == 0
                # Logger deve ter sido configurado com DEBUG
                mock_setup_logger.assert_called_with("doc_voz", level=10)  # DEBUG = 10
    
    def test_integration_file_extensions_validation(self):
        """Testa validação de extensões em fluxo completo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arquivo com extensão não suportada
            input_file = Path(temp_dir) / "test.pdf"
            input_file.write_text("Conteúdo PDF simulado")
            
            output_file = Path(temp_dir) / "output.mp3"
            
            with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                result = main()
            
            # Deve falhar com tipo não suportado
            assert result == 1
    
    def test_integration_output_directory_creation(self):
        """Testa criação de diretórios de saída."""
        with tempfile.TemporaryDirectory() as temp_dir:
            input_file = Path(temp_dir) / "test.txt" 
            input_file.write_text("Teste de criação de diretório")
            
            # Output em subdiretório que não existe
            output_file = Path(temp_dir) / "subdir" / "nested" / "output.mp3"
            
            with patch('src.tts.gtts_engine.gTTS') as mock_gtts:
                mock_tts_instance = Mock()
                mock_gtts.return_value = mock_tts_instance
                
                with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                    result = main()
                
                # Deve ter sucesso e criado os diretórios
                assert result == 0
                assert output_file.parent.exists()
    
    def test_integration_empty_file_handling(self):
        """Testa tratamento de arquivo vazio em fluxo completo."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Arquivo vazio
            input_file = Path(temp_dir) / "empty.txt"
            input_file.write_text("")
            
            output_file = Path(temp_dir) / "output.mp3"
            
            with patch('src.tts.gtts_engine.gTTS') as mock_gtts:
                mock_tts_instance = Mock()
                mock_gtts.return_value = mock_tts_instance
                
                with patch('sys.argv', ['main.py', str(input_file), str(output_file)]):
                    result = main()
                
                # Deve processar normalmente (string vazia)
                assert result == 0
                mock_gtts.assert_called_once_with("", lang="pt", slow=False)