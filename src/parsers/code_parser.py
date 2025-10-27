"""
Parser especializado para arquivos de código fonte.
Converte código em narrativa compreensível para áudio.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Tuple
import re
import ast
import tokenize
import io

from .base import Parser
from ..utils.logger import get_logger

logger = get_logger("code-parser")


class CodeParser(Parser):
    """Parser que converte código Python em narrativa explicativa para áudio."""
    
    SUPPORTED_EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.rb', '.go', '.php'}
    
    # Mapeamento de linguagens para extensões
    LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript', 
        '.ts': 'TypeScript',
        '.java': 'Java',
        '.cpp': 'C++',
        '.c': 'C',
        '.cs': 'C#',
        '.rb': 'Ruby',
        '.go': 'Go',
        '.php': 'PHP'
    }
    
    def __init__(self):
        self.indent_level = 0
        self.current_class = None
        self.current_function = None
    
    def can_parse(self, file_path: Path) -> bool:
        """Verifica se pode processar o arquivo baseado na extensão."""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS
    
    def parse(self, file_path: Path) -> str:
        """Converte arquivo de código em narrativa explicativa."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code_content = f.read()
            
            language = self.LANGUAGE_MAP.get(file_path.suffix.lower(), 'código')
            logger.info(f"Processando arquivo {language}: {file_path}")
            
            # Análise específica por linguagem
            if file_path.suffix.lower() == '.py':
                return self._parse_python_code(code_content, file_path)
            else:
                return self._parse_generic_code(code_content, file_path, language)
                
        except Exception as e:
            logger.error(f"Erro ao processar código: {e}")
            return f"Erro ao processar o arquivo de código: {str(e)}"
    
    def _parse_python_code(self, code: str, file_path: Path) -> str:
        """Análise especializada para código Python usando AST."""
        try:
            tree = ast.parse(code)
            narrative_parts = []
            
            # Cabeçalho
            narrative_parts.append(self._create_header(file_path, 'Python'))
            
            # Análise do docstring do módulo
            if (tree.body and isinstance(tree.body[0], ast.Expr) 
                and isinstance(tree.body[0].value, ast.Constant)
                and isinstance(tree.body[0].value.value, str)):
                docstring = tree.body[0].value.value
                narrative_parts.append(f"Descrição do módulo: {docstring}")
            
            # Análise de imports
            imports = self._extract_imports(tree)
            if imports:
                narrative_parts.append("Dependências importadas:")
                narrative_parts.extend(imports)
            
            # Análise de classes e funções
            narrative_parts.extend(self._analyze_python_structure(tree))
            
            # Análise linha por linha com contexto
            narrative_parts.append("\n--- Análise Detalhada do Código ---\n")
            narrative_parts.append(self._create_detailed_analysis(code))
            
            return "\n\n".join(narrative_parts)
            
        except SyntaxError as e:
            logger.warning(f"Erro de sintaxe Python, usando análise genérica: {e}")
            return self._parse_generic_code(code, file_path, 'Python')
    
    def _parse_generic_code(self, code: str, file_path: Path, language: str) -> str:
        """Análise genérica para qualquer linguagem de programação."""
        narrative_parts = []
        
        # Cabeçalho
        narrative_parts.append(self._create_header(file_path, language))
        
        # Análise de imports/includes
        imports = self._extract_generic_imports(code, language)
        if imports:
            narrative_parts.append("Dependências encontradas:")
            narrative_parts.extend(imports)
        
        # Análise estrutural genérica
        structure = self._analyze_generic_structure(code, language)
        if structure:
            narrative_parts.extend(structure)
        
        # Análise linha por linha
        narrative_parts.append("\n--- Análise Detalhada do Código ---\n")
        narrative_parts.append(self._create_detailed_analysis(code))
        
        return "\n\n".join(narrative_parts)
    
    def _create_header(self, file_path: Path, language: str) -> str:
        """Cria o cabeçalho explicativo do arquivo."""
        return f"""Análise do arquivo de código {language}: {file_path.name}

Este é um arquivo de código fonte escrito em {language}. 
Vamos analisar sua estrutura e funcionamento passo a passo."""
    
    def _extract_imports(self, tree: ast.AST) -> List[str]:
        """Extrai e explica imports Python."""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    name = alias.asname if alias.asname else alias.name
                    imports.append(f"Importa a biblioteca {alias.name} como {name}")
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or "módulo local"
                if node.names:
                    if len(node.names) == 1 and node.names[0].name == '*':
                        imports.append(f"Importa tudo do módulo {module}")
                    else:
                        items = [alias.name for alias in node.names]
                        imports.append(f"Do módulo {module}, importa: {', '.join(items)}")
        
        return imports
    
    def _extract_generic_imports(self, code: str, language: str) -> List[str]:
        """Extrai imports/includes de linguagens genéricas."""
        imports = []
        lines = code.split('\n')
        
        patterns = {
            'JavaScript': [r'^import\s+.*from\s+[\'"]([^\'"]+)[\'"]', r'^const\s+.*=\s+require\([\'"]([^\'"]+)[\'"]\)'],
            'TypeScript': [r'^import\s+.*from\s+[\'"]([^\'"]+)[\'"]'],
            'Java': [r'^import\s+([\w\.]+);'],
            'C++': [r'^#include\s*[<"]([^">]+)[">]'],
            'C': [r'^#include\s*[<"]([^">]+)[">]'],
            'C#': [r'^using\s+([\w\.]+);'],
            'Python': [r'^import\s+([\w\.]+)', r'^from\s+([\w\.]+)\s+import'],
            'Go': [r'^import\s+["]([^"]+)["]'],
            'PHP': [r'^require_once\s+[\'"]([^\'"]+)[\'"]', r'^include\s+[\'"]([^\'"]+)[\'"]']
        }
        
        if language in patterns:
            for line in lines:
                line = line.strip()
                for pattern in patterns[language]:
                    match = re.match(pattern, line)
                    if match:
                        imports.append(f"Importa/inclui: {match.group(1)}")
        
        return imports
    
    def _analyze_python_structure(self, tree: ast.AST) -> List[str]:
        """Analisa a estrutura de classes e funções Python com análise de propósito."""
        structure = []
        
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # Análise detalhada da classe
                class_analysis = self._analyze_class_purpose(node, tree)
                structure.append(f"\n=== Análise da Classe '{node.name}' ===")
                structure.append(f"Propósito geral: {class_analysis['purpose']}")
                
                if node.bases:
                    bases = [base.id if hasattr(base, 'id') else str(base) for base in node.bases]
                    structure.append(f"Herança: Esta classe herda de {', '.join(bases)}")
                
                # Docstring da classe
                if (node.body and isinstance(node.body[0], ast.Expr) 
                    and isinstance(node.body[0].value, ast.Constant)):
                    structure.append(f"Documentação: {node.body[0].value.value}")
                
                # Análise dos métodos
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                if methods:
                    structure.append(f"Métodos disponíveis:")
                    for method in methods:
                        method_purpose = self._analyze_method_purpose_from_ast(method)
                        structure.append(f"  - {method.name}: {method_purpose}")
                
                structure.append(f"Esta classe contém {len(methods)} métodos e implementa {class_analysis['features']}")
            
            elif isinstance(node, ast.FunctionDef):
                structure.append(f"\n=== Função '{node.name}' ===")
                
                # Análise de parâmetros
                if node.args.args:
                    args = [arg.arg for arg in node.args.args]
                    structure.append(f"Aceita os parâmetros: {', '.join(args)}")
                
                # Docstring da função
                if (node.body and isinstance(node.body[0], ast.Expr) 
                    and isinstance(node.body[0].value, ast.Constant)):
                    structure.append(f"Documentação: {node.body[0].value.value}")
                
                # Propósito da função
                func_purpose = self._analyze_method_purpose_from_ast(node)
                structure.append(f"Propósito: {func_purpose}")
        
        return structure
    
    def _analyze_class_purpose(self, class_node, tree):
        """Analisa o propósito geral de uma classe."""
        class_name = class_node.name
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]
        
        # Docstring da classe
        docstring = None
        if (class_node.body and isinstance(class_node.body[0], ast.Expr) 
            and isinstance(class_node.body[0].value, ast.Constant)):
            docstring = class_node.body[0].value.value
        
        # Análise baseada nos métodos
        features = []
        has_init = any(m.name == '__init__' for m in methods)
        has_str = any(m.name == '__str__' for m in methods)
        has_getters = any('get' in m.name.lower() for m in methods)
        has_setters = any('set' in m.name.lower() for m in methods)
        
        if has_init:
            features.append("inicialização de objetos")
        if has_str:
            features.append("representação em string")
        if has_getters or has_setters:
            features.append("acesso controlado a dados")
        
        # Determinar propósito baseado no nome e métodos
        purpose_parts = []
        
        if docstring:
            purpose_parts.append(docstring)
        else:
            # Inferir propósito baseado no nome
            name_lower = class_name.lower()
            if 'calculator' in name_lower or 'calc' in name_lower:
                purpose_parts.append("Esta classe implementa funcionalidades de cálculo matemático")
            elif 'manager' in name_lower:
                purpose_parts.append("Esta classe gerencia e coordena operações de um sistema")
            elif 'parser' in name_lower:
                purpose_parts.append("Esta classe processa e analisa dados de entrada")
            elif 'handler' in name_lower:
                purpose_parts.append("Esta classe manipula eventos ou requisições específicas")
            else:
                purpose_parts.append(f"Esta classe '{class_name}' implementa funcionalidades específicas do domínio")
        
        features_str = ", ".join(features) if features else "operações básicas"
        
        return {
            'purpose': ". ".join(purpose_parts),
            'features': features_str
        }
    
    def _analyze_method_purpose_from_ast(self, method_node):
        """Analisa o propósito de um método baseado no AST."""
        method_name = method_node.name
        
        # Docstring do método
        if (method_node.body and isinstance(method_node.body[0], ast.Expr) 
            and isinstance(method_node.body[0].value, ast.Constant)):
            return method_node.body[0].value.value
        
        # Análise baseada no nome
        if method_name == '__init__':
            return "inicializa uma nova instância da classe"
        elif method_name == '__str__':
            return "retorna representação textual do objeto"
        elif method_name.startswith('get_'):
            return f"obtém o valor de {method_name[4:]}"
        elif method_name.startswith('set_'):
            return f"define o valor de {method_name[4:]}"
        elif method_name.startswith('is_'):
            return f"verifica se {method_name[3:]}"
        elif method_name.startswith('can_'):
            return f"verifica se pode {method_name[4:]}"
        elif 'calculate' in method_name.lower():
            return "executa cálculos específicos"
        elif 'process' in method_name.lower():
            return "processa dados de entrada"
        else:
            return f"executa operação relacionada a {method_name}"
    
    def _analyze_generic_structure(self, code: str, language: str) -> List[str]:
        """Análise estrutural genérica baseada em padrões."""
        structure = []
        lines = code.split('\n')
        
        # Padrões comuns
        class_patterns = {
            'Java': r'^public\s+class\s+(\w+)',
            'C#': r'^public\s+class\s+(\w+)',
            'JavaScript': r'^class\s+(\w+)',
            'TypeScript': r'^class\s+(\w+)',
            'C++': r'^class\s+(\w+)',
            'PHP': r'^class\s+(\w+)'
        }
        
        function_patterns = {
            'JavaScript': r'^function\s+(\w+)\s*\(',
            'TypeScript': r'^function\s+(\w+)\s*\(',
            'Java': r'^\s*public\s+.*\s+(\w+)\s*\(',
            'C++': r'^\s*\w+\s+(\w+)\s*\(',
            'C#': r'^\s*public\s+.*\s+(\w+)\s*\(',
            'PHP': r'^function\s+(\w+)\s*\(',
            'Go': r'^func\s+(\w+)\s*\('
        }
        
        # Buscar classes
        if language in class_patterns:
            pattern = class_patterns[language]
            for line in lines:
                match = re.search(pattern, line.strip())
                if match:
                    structure.append(f"Classe '{match.group(1)}' encontrada")
        
        # Buscar funções
        if language in function_patterns:
            pattern = function_patterns[language]
            for line in lines:
                match = re.search(pattern, line.strip())
                if match:
                    structure.append(f"Função '{match.group(1)}' encontrada")
        
        return structure
    
    def _create_detailed_analysis(self, code: str) -> str:
        """Cria análise linha por linha do código de forma inteligente."""
        lines = code.split('\n')
        analysis_parts = []
        
        in_class = False
        in_method = False
        current_method_lines = []
        method_start_line = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            line_number = i + 1
            
            # Pular linhas vazias
            if not stripped:
                i += 1
                continue
            
            # Detectar início de classe
            if stripped.startswith('class '):
                if in_method:
                    # Finalizar método anterior
                    self._add_method_analysis(analysis_parts, current_method_lines, method_start_line, lines)
                    in_method = False
                    current_method_lines = []
                
                class_line = self._describe_line_naturally(line, line_number)
                analysis_parts.append(class_line)
                analysis_parts.append(f"Explicação: {self._explain_code_line(stripped, line_number)}")
                analysis_parts.append("")
                in_class = True
                i += 1
                continue
            
            # Detectar início de método/função
            elif stripped.startswith('def '):
                if in_method:
                    # Finalizar método anterior
                    self._add_method_analysis(analysis_parts, current_method_lines, method_start_line, lines)
                
                # Iniciar novo método
                in_method = True
                current_method_lines = [line]
                method_start_line = line_number
                i += 1
                continue
            
            # Se estamos dentro de um método, acumular linhas
            elif in_method:
                current_method_lines.append(line)
                i += 1
                continue
            
            # Linha normal (fora de método)
            else:
                if in_method:
                    # Finalizar método
                    self._add_method_analysis(analysis_parts, current_method_lines, method_start_line, lines)
                    in_method = False
                    current_method_lines = []
                
                line_description = self._describe_line_naturally(line, line_number)
                analysis_parts.append(line_description)
                
                explanation = self._explain_code_line(stripped, line_number)
                if explanation:
                    analysis_parts.append(f"Explicação: {explanation}")
                analysis_parts.append("")
                i += 1
        
        # Finalizar último método se existir
        if in_method and current_method_lines:
            self._add_method_analysis(analysis_parts, current_method_lines, method_start_line, lines)
        
        return "\n".join(analysis_parts)
    
    def _narrate_line_literally(self, line: str, line_number: int) -> str:
        """Narra a linha literalmente, falando todos os caracteres especiais."""
        if not line.strip():
            return None
            
        # Verificar se é linha de string tripla vazia ou de fechamento
        stripped = line.strip()
        if stripped in ['"""', "'''"]:
            return f"Linha {line_number}: {stripped.replace('\"', 'aspas duplas')}"
        
        # Criar narração literal da linha
        literal_parts = [f"Linha {line_number}:"]
        
        # Tratar indentação primeiro
        indent_count = len(line) - len(line.lstrip())
        if indent_count > 0:
            if line[0] == ' ':
                literal_parts.append(f"indentação de {indent_count} espaços")
            elif line[0] == '\t':
                tab_count = 0
                for char in line:
                    if char == '\t':
                        tab_count += 1
                    else:
                        break
                literal_parts.append(f"indentação de {tab_count} tabs")
        
        # Processar o resto da linha token por token
        content = line.strip()
        i = 0
        
        while i < len(content):
            # Tratar strings triplas
            if i <= len(content) - 3 and content[i:i+3] in ['"""', "'''"]:
                quote_type = content[i:i+3]
                string_content = ""
                i += 3  # Pular aspas inicial
                
                # Verificar se é docstring de uma linha
                end_pos = content.find(quote_type, i)
                if end_pos != -1:
                    string_content = content[i:end_pos]
                    i = end_pos + 3
                    literal_parts.append(f"docstring {string_content}")
                else:
                    # String tripla que continua em outras linhas
                    string_content = content[i:]
                    literal_parts.append(f"início de docstring {string_content}")
                    break
                continue
            
            # Tratar strings simples
            elif content[i] in ['"', "'"]:
                quote_type = content[i]
                string_content = ""
                i += 1  # Pular aspas inicial
                
                while i < len(content) and content[i] != quote_type:
                    string_content += content[i]
                    i += 1
                
                if i < len(content):  # Se encontrou aspas final
                    i += 1  # Pular aspas final
                
                literal_parts.append(f"string {string_content}")
                continue
            
            # Tratar comentários
            elif content[i] == '#':
                comment_content = content[i+1:].strip()
                literal_parts.append(f"comentário {comment_content}")
                break
            
            # Tratar palavras e identificadores
            elif content[i].isalpha() or content[i] == '_':
                word = ""
                while i < len(content) and (content[i].isalnum() or content[i] == '_'):
                    word += content[i]
                    i += 1
                
                # Tratar underscores especiais
                if '__' in word:
                    word_parts = []
                    j = 0
                    while j < len(word):
                        if j < len(word) - 1 and word[j:j+2] == '__':
                            word_parts.append("duplo underscore")
                            j += 2
                        elif word[j] == '_':
                            word_parts.append("underscore")
                            j += 1
                        else:
                            # Pegar palavra normal
                            normal_word = ""
                            while j < len(word) and word[j] != '_':
                                normal_word += word[j]
                                j += 1
                            if normal_word:
                                word_parts.append(normal_word)
                    literal_parts.extend(word_parts)
                else:
                    literal_parts.append(word.replace('_', ' underscore '))
                continue
            
            # Tratar números
            elif content[i].isdigit():
                number = ""
                while i < len(content) and (content[i].isdigit() or content[i] == '.'):
                    number += content[i]
                    i += 1
                literal_parts.append(number)
                continue
            
            # Símbolos especiais
            elif content[i] == '(':
                literal_parts.append("abre parênteses")
            elif content[i] == ')':
                literal_parts.append("fecha parênteses")
            elif content[i] == '{':
                literal_parts.append("abre chaves")
            elif content[i] == '}':
                literal_parts.append("fecha chaves")
            elif content[i] == '[':
                literal_parts.append("abre colchetes")
            elif content[i] == ']':
                literal_parts.append("fecha colchetes")
            elif content[i] == ':':
                literal_parts.append("dois pontos")
            elif content[i] == ';':
                literal_parts.append("ponto e vírgula")
            elif content[i] == '=':
                # Verificar operadores compostos
                if i < len(content) - 1 and content[i+1] == '=':
                    literal_parts.append("duplo igual")
                    i += 1
                else:
                    literal_parts.append("igual")
            elif content[i] == '+':
                literal_parts.append("mais")
            elif content[i] == '-':
                literal_parts.append("menos")
            elif content[i] == '*':
                literal_parts.append("asterisco")
            elif content[i] == '/':
                literal_parts.append("barra")
            elif content[i] == '<':
                literal_parts.append("menor que")
            elif content[i] == '>':
                literal_parts.append("maior que")
            elif content[i] == '.':
                literal_parts.append("ponto")
            elif content[i] == ',':
                literal_parts.append("vírgula")
            elif content[i] == ' ':
                literal_parts.append("espaço")
            else:
                literal_parts.append(content[i])
            
            i += 1
        
        return " ".join(literal_parts)
    
    def _describe_line_naturally(self, line: str, line_number: int) -> str:
        """Descreve uma linha de código de forma natural, sem soletrar."""
        stripped = line.strip()
        if not stripped:
            return None
        
        indent = len(line) - len(line.lstrip())
        indent_desc = f"com indentação de {indent} espaços" if indent > 0 else ""
        
        # Identificar o tipo de linha e descrever naturalmente
        description = f"Linha {line_number}"
        if indent_desc:
            description += f" {indent_desc}"
        description += f": {stripped}"
        
        return description
    
    def _add_method_analysis(self, analysis_parts, method_lines, start_line, all_lines):
        """Adiciona análise completa de um método."""
        if not method_lines:
            return
        
        # Linha de definição do método
        method_def = method_lines[0].strip()
        analysis_parts.append(f"\n--- Análise do Método (linha {start_line}) ---")
        analysis_parts.append(f"Definição: {method_def}")
        analysis_parts.append(f"Explicação: {self._explain_code_line(method_def, start_line)}")
        analysis_parts.append("")
        
        # Analisar cada linha do método
        for i, line in enumerate(method_lines[1:], 1):
            line_num = start_line + i
            stripped = line.strip()
            if not stripped:
                continue
            
            # Descrever a linha
            line_desc = self._describe_line_naturally(line, line_num)
            analysis_parts.append(line_desc)
            
            # Explicar a linha
            explanation = self._explain_code_line(stripped, line_num)
            if explanation:
                analysis_parts.append(f"Explicação: {explanation}")
            analysis_parts.append("")
        
        # Resumo do propósito do método
        method_purpose = self._analyze_method_purpose(method_lines)
        if method_purpose:
            analysis_parts.append(f"Propósito do método: {method_purpose}")
            analysis_parts.append("")
    
    def _analyze_method_purpose(self, method_lines):
        """Analisa o propósito geral de um método baseado em suas linhas."""
        if not method_lines:
            return None
        
        method_def = method_lines[0].strip()
        method_name = ""
        
        # Extrair nome do método
        if method_def.startswith('def '):
            method_name = method_def.split('(')[0].replace('def ', '').strip()
        
        # Buscar docstring nas primeiras linhas
        docstring = None
        for line in method_lines[1:4]:  # Verificar até 3 linhas após def
            stripped = line.strip()
            if '"""' in stripped or "'''" in stripped:
                # Extrair docstring
                if stripped.startswith('"""') and stripped.endswith('"""') and len(stripped) > 6:
                    docstring = stripped[3:-3].strip()
                elif stripped.startswith("'''") and stripped.endswith("'''") and len(stripped) > 6:
                    docstring = stripped[3:-3].strip()
                break
        
        # Análise baseada no nome e conteúdo
        purposes = []
        
        if method_name == '__init__':
            purposes.append("Este é o método construtor que inicializa uma nova instância da classe")
        elif method_name.startswith('__') and method_name.endswith('__'):
            purposes.append(f"Este é um método especial (dunder method) {method_name} usado pelo Python internamente")
        elif 'return' in ' '.join(method_lines):
            purposes.append("Este método retorna um valor após processar os dados")
        else:
            purposes.append("Este método executa uma operação específica")
        
        if docstring:
            purposes.append(f"Documentação: {docstring}")
        
        # Analisar operações baseadas no conteúdo
        content = ' '.join(method_lines).lower()
        if 'print' in content:
            purposes.append("realiza saída de dados")
        if any(op in content for op in ['+', '-', '*', '/']):
            purposes.append("executa cálculos matemáticos")
        if 'if' in content:
            purposes.append("contém lógica condicional")
        if 'for' in content or 'while' in content:
            purposes.append("realiza iterações ou loops")
        
        return ". ".join(purposes) if purposes else None
    
    def _explain_code_line(self, line: str, line_number: int) -> str:
        """Explica uma linha específica de código após a narração literal."""
        line = line.strip()
        
        # Padrões comuns e suas explicações mais detalhadas
        explanations = [
            (r'^import\s+(.+)', lambda m: f"Esta linha importa a biblioteca ou módulo {m.group(1)} para uso no código"),
            (r'^from\s+(.+)\s+import\s+(.+)', lambda m: f"Esta linha importa elementos específicos {m.group(2)} do módulo {m.group(1)}"),
            (r'^def\s+(__\w+__)\s*\((.*)\):', lambda m: f"Define um método especial (dunder method) {m.group(1)}, usado pelo Python para operações internas, com parâmetros {m.group(2) or 'apenas self'}"),
            (r'^def\s+(\w+)\s*\((.*)\):', lambda m: f"Define uma função ou método chamado {m.group(1)} que recebe os parâmetros {m.group(2) or 'nenhum parâmetro'}"),
            (r'^class\s+(\w+)(?:\(([^)]+)\))?.*:', lambda m: f"Define uma classe chamada {m.group(1)}{' que herda de ' + m.group(2) if m.group(2) else ''}, criando um novo tipo de objeto"),
            (r'^if\s+(.+):', lambda m: f"Estrutura condicional que executa o bloco seguinte apenas se a condição {m.group(1)} for verdadeira"),
            (r'^elif\s+(.+):', lambda m: f"Condição alternativa que é verificada apenas se as condições anteriores forem falsas, testa se {m.group(1)}"),
            (r'^else:', lambda m: "Bloco que executa quando todas as condições anteriores do if/elif foram falsas"),
            (r'^for\s+(.+)\s+in\s+(.+):', lambda m: f"Loop que itera sobre cada elemento, onde {m.group(1)} representa cada item de {m.group(2)}"),
            (r'^while\s+(.+):', lambda m: f"Loop que continua executando enquanto a condição {m.group(1)} permanecer verdadeira"),
            (r'^return\s+(.+)', lambda m: f"Retorna o valor {m.group(1)} e encerra a execução da função"),
            (r'^return\s*$', lambda m: "Retorna sem valor (None) e encerra a execução da função"),
            (r'^self\.(\w+)\s*=\s*(.+)', lambda m: f"Atribui o valor {m.group(2)} ao atributo de instância {m.group(1)} do objeto atual"),
            (r'^(\w+)\s*=\s*(.+)', lambda m: f"Cria ou atualiza a variável {m.group(1)} com o valor {m.group(2)}"),
            (r'^(\w+)\.(\w+)\s*\((.*)\)', lambda m: f"Chama o método {m.group(2)} do objeto {m.group(1)} passando os argumentos {m.group(3) or 'nenhum'}"),
            (r'^print\s*\((.+)\)', lambda m: f"Exibe no console ou saída padrão o conteúdo de {m.group(1)}"),
            (r'^try:', lambda m: "Inicia um bloco de tratamento de exceções, tentando executar código que pode gerar erros"),
            (r'^except\s+(\w+).*:', lambda m: f"Captura e trata especificamente exceções do tipo {m.group(1)}"),
            (r'^except\s*:', lambda m: "Captura qualquer tipo de exceção que possa ocorrer no bloco try"),
            (r'^finally:', lambda m: "Bloco que sempre executa, independente de ter ocorrido exceção ou não"),
            (r'^raise\s+(.+)', lambda m: f"Lança uma exceção {m.group(1)}, interrompendo o fluxo normal"),
            (r'^with\s+(.+)\s+as\s+(\w+):', lambda m: f"Usa o gerenciador de contexto {m.group(1)} e o nomeia como {m.group(2)}"),
            (r'^@(\w+)', lambda m: f"Decorador {m.group(1)} que modifica o comportamento da função ou classe seguinte"),
            (r'^\s*"""(.*)"""', lambda m: f"Docstring de uma linha que documenta: {m.group(1)}"),
            (r'^\s*#(.+)', lambda m: f"Comentário explicativo: {m.group(1).strip()}"),
        ]
        
        for pattern, explanation_func in explanations:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                return explanation_func(match)
        
        # Explicações genéricas para outros casos
        if '=' in line and not any(op in line for op in ['==', '!=', '<=', '>=']):
            return "Esta linha realiza uma atribuição de valor a uma variável"
        elif line.endswith(':'):
            return "Esta linha inicia um novo bloco de código que deve ser indentado"
        elif any(keyword in line for keyword in ['if', 'elif', 'else', 'for', 'while', 'try', 'except']):
            return "Esta linha contém uma estrutura de controle de fluxo"
        else:
            return "Esta linha executa uma operação ou chamada de função"