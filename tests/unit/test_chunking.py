"""
Teste para validar a funcionalidade de chunking do GTTSEngine.
"""
import tempfile
import os
from pathlib import Path
import sys

# Adicionar src ao path para importar módulos
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.tts.gtts_engine import GTTSEngine

def test_chunking():
    """Testa o chunking com diferentes tamanhos de texto."""
    engine = GTTSEngine()
    
    # Teste 1: Texto pequeno (não deve usar chunking)
    texto_pequeno = "Este é um texto pequeno para teste."
    print(f"Teste 1 - Texto pequeno ({len(texto_pequeno)} chars)")
    chunks = engine._split_text_intelligently(texto_pequeno)
    print(f"Resultado: {len(chunks)} chunks")
    assert len(chunks) == 1
    print("✅ Teste 1 passou\n")
    
    # Teste 2: Texto médio (deve usar chunking)
    texto_medio = "A " * 3000  # 6000 caracteres
    print(f"Teste 2 - Texto médio ({len(texto_medio)} chars)")
    chunks = engine._split_text_intelligently(texto_medio)
    print(f"Resultado: {len(chunks)} chunks")
    assert len(chunks) > 1
    print("✅ Teste 2 passou\n")
    
    # Teste 3: Texto com pontuação (deve quebrar em sentenças)
    texto_pontuado = ("Esta é uma sentença. " * 200) + ("Esta é outra sentença! " * 200)
    print(f"Teste 3 - Texto com pontuação ({len(texto_pontuado)} chars)")
    chunks = engine._split_text_intelligently(texto_pontuado)
    print(f"Resultado: {len(chunks)} chunks")
    print(f"Primeiro chunk termina com: '{chunks[0][-20:]}'")
    assert len(chunks) > 1
    print("✅ Teste 3 passou\n")
    
    # Teste 4: Verificar ponto de quebra
    texto_teste = "Palavra " * 1000  # Texto sem pontuação
    print(f"Teste 4 - Encontrar ponto de quebra ({len(texto_teste)} chars)")
    ponto = engine._find_best_split_point(texto_teste[:engine.MAX_CHUNK_SIZE])
    print(f"Ponto de quebra encontrado: {ponto}")
    print("✅ Teste 4 passou\n")
    
    print("🎉 Todos os testes passaram!")

if __name__ == "__main__":
    test_chunking()