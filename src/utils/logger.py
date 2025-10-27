import logging
from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """Cria e retorna um logger com RichHandler. Idempotente (reusa handlers existentes).

    Args:
        name: nome do logger
    Returns:
        logging.Logger
    """
    logger = logging.getLogger(name)
    # evita adicionar handlers duplicados se o logger já foi configurado
    if logger.handlers:
        return logger

    handler = RichHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
