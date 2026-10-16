import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para garantir resolução correta de módulos internos
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server.mcpserver import MCPServer

# Definição do Sandbox de Segurança: 
# Fixa o limite de atuação da IA no diretório de trabalho atual (onde o script foi chamado).
ALLOWED_WORKSPACE = Path(os.getcwd()).resolve()

# Inicialização do servidor MCP
mcp = MCPServer("Filesystem_Server")

def _validate_path(target_path: str) -> Path:
    """
    Verifica se o caminho solicitado está dentro do workspace permitido.
    Previne ataques ou alucinações de 'Path Traversal' (ex: ../../../Windows/System32).
    """
    requested_path = Path(target_path).resolve()
    
    # A função is_relative_to verifica hierarquicamente se a rota faz parte do workspace
    if not requested_path.is_relative_to(ALLOWED_WORKSPACE):
        raise PermissionError(
            f"Acesso negado por sandboxing. O caminho '{requested_path}' "
            f"está fora do workspace permitido ({ALLOWED_WORKSPACE})."
        )
    return requested_path

@mcp.tool()
def list_directory(directory_path: str = ".") -> str:
    """
    Lista todos os arquivos e pastas em um diretório específico dentro do workspace.
    Utilize esta ferramenta para entender a estrutura do projeto antes de ler ou escrever código.
    """
    try:
        safe_path = _validate_path(directory_path)
        if not safe_path.exists() or not safe_path.is_dir():
            return f"Erro: O diretório '{directory_path}' não existe ou não é uma pasta válida."
        
        items = os.listdir(safe_path)
        if not items:
            return f"O diretório '{safe_path}' está vazio."
            
        return f"Conteúdo de {safe_path}:\n" + "\n".join(f"- {item}" for item in items)
    except Exception as e:
        return f"Erro ao listar diretório: {str(e)}"

@mcp.tool()
def read_file(file_path: str) -> str:
    """
    Lê e retorna o conteúdo exato de um arquivo de texto, script ou código-fonte.
    Utilize para inspecionar o código antes de sugerir refatorações.
    """
    try:
        safe_path = _validate_path(file_path)
        if not safe_path.exists() or not safe_path.is_file():
            return f"Erro: O arquivo '{file_path}' não foi encontrado."
        
        with open(safe_path, "r", encoding="utf-8") as file_descriptor:
            content = file_descriptor.read()
        return content
    except UnicodeDecodeError:
        return "Erro: O arquivo parece ser um binário ou possui uma codificação não suportada (esperado UTF-8)."
    except Exception as e:
        return f"Erro ao ler o arquivo: {str(e)}"

@mcp.tool()
def write_file(file_path: str, content: str) -> str:
    """
    Cria um novo arquivo ou sobrescreve um existente com o conteúdo fornecido.
    Atenção: O conteúdo enviado substituirá tudo o que houver no arquivo.
    """
    try:
        safe_path = _validate_path(file_path)
        
        # Cria as pastas pai (diretórios intermediários) automaticamente, caso não existam
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(safe_path, "w", encoding="utf-8") as file_descriptor:
            file_descriptor.write(content)
        return f"Sucesso: Arquivo gravado com êxito em '{safe_path}'."
    except Exception as e:
        return f"Erro ao gravar no arquivo: {str(e)}"

if __name__ == "__main__":
    # Logs operacionais injetados no stderr para não corromper o canal de dados (stdio) do MCP
    print(f"[INFO] Filesystem MCP Server ativo. Workspace confinado em: {ALLOWED_WORKSPACE}", file=sys.stderr)
    mcp.run()