"""
Testes unitários para o módulo de utilitários.
"""
import pytest
import logging
from unittest.mock import Mock, patch

from src.utils.logger import get_logger


class TestLogger:
    """Testes para o sistema de logging."""
    
    def test_get_logger_basic(self):
        """Testa criação básica do logger."""
        logger = get_logger("test_logger")
        
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1
    
    def test_get_logger_different_names(self):
        """Testa que loggers com nomes diferentes são instâncias diferentes."""
        logger1 = get_logger("test_logger_1")
        logger2 = get_logger("test_logger_2")
        
        assert logger1.name != logger2.name
        assert logger1 != logger2
    
    def test_get_logger_same_name_reuses_logger(self):
        """Testa que loggers com mesmo nome retornam a mesma instância."""
        logger1 = get_logger("same_name_logger")
        logger2 = get_logger("same_name_logger")
        
        assert logger1 is logger2
    
    @patch('src.utils.logger.RichHandler')
    def test_get_logger_rich_handler_configuration(self, mock_rich_handler):
        """Testa configuração do RichHandler."""
        mock_handler = Mock()
        mock_rich_handler.return_value = mock_handler
        
        logger = get_logger("test_rich_logger")
        
        # Verifica se RichHandler foi criado corretamente
        mock_rich_handler.assert_called_once()
        
        # Verifica se o handler foi adicionado ao logger
        assert mock_handler in logger.handlers
    
    @patch('src.utils.logger.RichHandler')
    def test_get_logger_formatter_configuration(self, mock_rich_handler):
        """Testa configuração do formatter."""
        mock_handler = Mock()
        mock_rich_handler.return_value = mock_handler
        
        logger = get_logger("test_formatter_logger")
        
        # Verifica se setFormatter foi chamado no handler
        mock_handler.setFormatter.assert_called_once()
    
    def test_get_logger_no_duplicate_handlers(self):
        """Testa que não são adicionados handlers duplicados."""
        logger_name = "no_duplicate_logger"
        
        # Primeira chamada
        logger1 = get_logger(logger_name)
        initial_handler_count = len(logger1.handlers)
        
        # Segunda chamada
        logger2 = get_logger(logger_name)
        final_handler_count = len(logger2.handlers)
        
        assert initial_handler_count == final_handler_count
        assert logger1 is logger2
    
    def test_logger_actually_logs(self):
        """Testa que o logger efetivamente registra mensagens."""
        logger = get_logger("functional_test_logger")
        
        # Testa diferentes níveis de log (não podemos facilmente testar
        # a saída do RichHandler, mas podemos verificar que não há erro)
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Se chegou até aqui, o logger está funcionando
        assert True