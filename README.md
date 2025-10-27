# 🎙️ DocuVoz - Conversor de Texto para Áudio

> 🚀 **Aplicação CLI moderna em Python que transforma seus documentos em áudio!**

DocuVoz é uma ferramenta poderosa e modular que converte documentos (.txt e .docx) em arquivos de áudio (MP3/WAV). Desenvolvida com arquitetura limpa usando padrões **Factory** e **Strategy** para máxima extensibilidade.

## ✨ Características

- 📝 **Suporte a múltiplos formatos**: TXT e DOCX (expansível para PDF, etc.)
- 🎵 **Múltiplas engines de voz**: gTTS (online) e pyttsx3 (offline)
- 🏗️ **Arquitetura modular**: Fácil de estender com novos formatos e vozes
- 🎨 **Interface elegante**: CLI com logging colorido usando Rich
- 🌐 **Multiplataforma**: Windows, macOS e Linux
- 🆓 **Totalmente gratuito** e open source

---

## 📋 Pré-requisitos

### 🖥️ Para Windows
- Python 3.8+ ([Download aqui](https://www.python.org/downloads/))
- Git ([Download aqui](https://git-scm.com/download/win))

### 🐧 Para Linux (Ubuntu/Debian)
- Python 3.8+ (geralmente já instalado)
- Git (geralmente já instalado)

---

## 🚀 Guia de Instalação Passo-a-Passo

### 🔽 Passo 1: Clone o Repositório

Abra seu terminal/prompt de comando e execute:

```bash
git clone https://github.com/M41k0n-Mk/doc-voz.git
cd doc-voz
```

### 🐧 Passo 2: Configuração Linux (Apenas para Linux)

Se você estiver no Linux, instale as dependências de áudio:

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip espeak ffmpeg libasound2-dev
```

### 🔧 Passo 3: Criar Ambiente Virtual

#### 🖥️ Windows:
```cmd
python -m venv .venv
.venv\Scripts\activate
```

#### 🐧 Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> 💡 **Dica**: Você verá `(.venv)` no início da linha do terminal indicando que o ambiente virtual está ativo!

### 📦 Passo 4: Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

⏳ **Aguarde**: Isso pode levar alguns minutos na primeira vez.

---

## 🎯 Como Usar

### 📝 Passo 1: Prepare seu Arquivo

Crie um arquivo de texto simples ou use o arquivo de exemplo já incluído:

```bash
# Use o arquivo de exemplo incluído
ls arquivo_teste.txt
```

Ou crie seu próprio arquivo `.txt` ou `.docx` com o conteúdo que deseja converter.

### 🎵 Passo 2: Gerar Áudio

#### 🌐 **Opção 1: gTTS (Recomendado) - Requer Internet**
```bash
python -m src.main arquivo_teste.txt --engine gtts
```

#### 💻 **Opção 2: pyttsx3 (Offline)**
```bash
python -m src.main arquivo_teste.txt --engine pyttsx3
```

#### 🎛️ **Opção 3: Arquivo de Saída Personalizado**
```bash
python -m src.main arquivo_teste.txt --engine gtts --output meu_audio.mp3
```

### 🎧 Passo 3: Reproduzir o Áudio

Seu arquivo de áudio estará em:
- 📁 `out/nome_do_arquivo.mp3` (para gTTS)
- 📁 `out/nome_do_arquivo.wav` (para pyttsx3)

Abra com qualquer player de áudio do seu sistema!

---

## 📚 Exemplos Práticos

### 📖 Converter Documento Word
```bash
python -m src.main meu_documento.docx --engine gtts
```

### 🎙️ Voz Offline (sem internet)
```bash
python -m src.main meu_texto.txt --engine pyttsx3
```

### 📂 Saída Personalizada
```bash
python -m src.main livro.txt --engine gtts --output audiobook/capitulo1.mp3
```

---

## 🛠️ Solução de Problemas

### ❌ "Arquivo não encontrado"
- ✅ Verifique se o arquivo existe no diretório atual
- ✅ Use caminhos completos: `python -m src.main /caminho/completo/arquivo.txt`

### ❌ "No module named 'src'"
- ✅ Certifique-se de estar no diretório do projeto (`cd doc-voz`)
- ✅ Verifique se o ambiente virtual está ativo (`(.venv)` no terminal)

### ❌ Problemas com pyttsx3 no Linux
- ✅ Use gTTS como alternativa: `--engine gtts`
- ✅ Instale dependências adicionais: `sudo apt install espeak espeak-data`

### 🌐 Problemas de Conexão com gTTS
- ✅ Verifique sua conexão com a internet
- ✅ Use pyttsx3 como alternativa offline: `--engine pyttsx3`

---

## 🏗️ Estrutura do Projeto

```
doc-voz/
├── 📄 README.md              # Este arquivo
├── 📋 requirements.txt       # Dependências Python
├── 📝 arquivo_teste.txt      # Arquivo de exemplo
├── 📁 out/                   # Arquivos de áudio gerados
├── 📁 src/                   # Código fonte
│   ├── 🐍 main.py           # Interface CLI principal
│   ├── 📁 parsers/          # Leitores de arquivo
│   │   ├── 🏭 factory.py    # Factory Pattern
│   │   ├── 📄 txt_parser.py # Leitor .txt
│   │   └── 📄 docx_parser.py# Leitor .docx
│   ├── 📁 tts/              # Engines de voz
│   │   ├── 🌐 gtts_engine.py    # Google TTS
│   │   └── 💻 pyttsx3_engine.py # Engine offline
│   └── 📁 utils/            # Utilitários
│       └── 📊 logger.py     # Sistema de logs
```

---

## 🚀 Recursos Avançados

### 🎛️ Opções da Linha de Comando

```bash
python -m src.main --help
```

**Parâmetros disponíveis:**
- `input`: Arquivo de entrada (.txt ou .docx)
- `--engine`: Engine TTS (`gtts` ou `pyttsx3`)
- `--output`: Arquivo de saída personalizado

### 🔧 Personalizações

O código foi desenvolvido com padrões de design que facilitam extensões:

- **➕ Novos formatos**: Adicione parsers em `src/parsers/`
- **🎙️ Novas vozes**: Implemente engines em `src/tts/`
- **🌐 APIs externas**: ElevenLabs, Azure Speech, etc.

---

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. 🍴 Fork o projeto
2. 🌿 Crie uma branch (`git checkout -b feature/AmazingFeature`)
3. 📝 Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push para a branch (`git push origin feature/AmazingFeature`)
5. 🔁 Abra um Pull Request

---

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

---

## 👨‍💻 Autor

Desenvolvido com ❤️ por **M41k0n-Mk**

- 📧 **Issues**: [GitHub Issues](https://github.com/M41k0n-Mk/doc-voz/issues)
- 🐛 **Bugs**: Reporte problemas via Issues
- 💡 **Sugestões**: Contribuições e ideias são sempre bem-vindas!

---

## ⭐ Gostou do Projeto?

Se este projeto foi útil para você, considere dar uma ⭐ no repositório!

**Compartilhe com seus amigos e colegas! 🚀**
