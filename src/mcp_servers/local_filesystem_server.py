import os
import sys
from pathlib import Path

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("Local_Filesystem_Server")

CAMINHOS_SENSIVEIS = [
    "Windows",
    "System32",
    "SysWOW64",
    "bootmgr",
    "pagefile.sys",
    "hiberfil.sys",
    "/etc/",
    "/var/",
    "/usr/",
    "/bin/",
    "/sbin/",
    "/root/",
]


def _resolver_caminho(caminho_bruto: str) -> Path:
    """
    Resolve variáveis de ambiente, diretório do utilizador (~) e caminhos relativos
    para um caminho absoluto no sistema de arquivos local.
    """
    expandido = os.path.expanduser(os.path.expandvars(caminho_bruto))
    return Path(expandido).resolve()


def _verificar_caminho_sensivel(caminho: Path) -> bool:
    """
    Verifica se o caminho aponta para áreas sensíveis do sistema operativo.
    Retorna True se for considerado sensível.
    """
    caminho_str = str(caminho).replace("\\", "/")
    for padrao in CAMINHOS_SENSIVEIS:
        if padrao.lower() in caminho_str.lower():
            return True
    return False


@mcp.tool()
def listar_arquivos(caminho: str) -> str:
    """
    Lista arquivos e pastas de um diretório local informado pelo utilizador.

    Args:
        caminho (str): Caminho da pasta (exemplo: C:\\Utilizador\\Documentos ou ~/Documentos).

    Returns:
        str: Lista de itens ou mensagem de erro.
    """
    try:
        caminho_resolvido = _resolver_caminho(caminho)
        if not caminho_resolvido.exists() or not caminho_resolvido.is_dir():
            return f"Erro: O diretório '{caminho}' não existe ou não é uma pasta válida."
        itens = os.listdir(caminho_resolvido)
        if not itens:
            return f"O diretório '{caminho_resolvido}' está vazio."
        return f"Conteúdo de {caminho_resolvido}:\n" + "\n".join(f"- {item}" for item in itens)
    except Exception as e:
        return f"Erro ao listar diretório: {str(e)}"


@mcp.tool()
def ler_arquivo(caminho: str) -> str:
    """
    Lê e retorna o conteúdo de um arquivo local informado pelo utilizador.

    Args:
        caminho (str): Caminho completo do arquivo.

    Returns:
        str: Conteúdo do arquivo ou mensagem de erro.
    """
    try:
        caminho_resolvido = _resolver_caminho(caminho)
        if not caminho_resolvido.exists() or not caminho_resolvido.is_file():
            return f"Erro: O arquivo '{caminho}' não foi encontrado."
        with open(caminho_resolvido, "r", encoding="utf-8") as descritor_arquivo:
            conteudo = descritor_arquivo.read()
        return conteudo
    except UnicodeDecodeError:
        return "Erro: O arquivo parece ser binário ou possui codificação não suportada (esperado UTF-8)."
    except Exception as e:
        return f"Erro ao ler o arquivo: {str(e)}"


@mcp.tool()
def salvar_arquivo(caminho: str, conteudo: str) -> str:
    """
    Cria um novo arquivo ou sobrescreve um existente com o conteúdo fornecido pelo utilizador.

    Args:
        caminho (str): Caminho completo do arquivo de destino.
        conteudo (str): Texto a ser gravado no arquivo.

    Returns:
        str: Mensagem de sucesso ou erro.
    """
    try:
        caminho_resolvido = _resolver_caminho(caminho)
        if _verificar_caminho_sensivel(caminho_resolvido):
            return f"Erro: Operação bloqueada. O caminho '{caminho}' aponta para uma área sensível do sistema."
        caminho_resolvido.parent.mkdir(parents=True, exist_ok=True)
        with open(caminho_resolvido, "w", encoding="utf-8") as descritor_arquivo:
            descritor_arquivo.write(conteudo)
        return f"Sucesso: Arquivo gravado em '{caminho_resolvido}'."
    except Exception as e:
        return f"Erro ao gravar no arquivo: {str(e)}"


@mcp.tool()
def alterar_arquivo(caminho: str, conteudo: str) -> str:
    """
    Altera o conteúdo de um arquivo existente (sobrescreve integralmente).
    Utilizado apenas quando o utilizador solicita explicitamente a alteração.

    Args:
        caminho (str): Caminho completo do arquivo a ser alterado.
        conteudo (str): Novo conteúdo do arquivo.

    Returns:
        str: Mensagem de sucesso ou erro.
    """
    try:
        caminho_resolvido = _resolver_caminho(caminho)
        if not caminho_resolvido.exists() or not caminho_resolvido.is_file():
            return f"Erro: O arquivo '{caminho}' não foi encontrado."
        if _verificar_caminho_sensivel(caminho_resolvido):
            return f"Erro: Operação bloqueada. O caminho '{caminho}' aponta para uma área sensível do sistema."
        with open(caminho_resolvido, "w", encoding="utf-8") as descritor_arquivo:
            descritor_arquivo.write(conteudo)
        return f"Sucesso: Arquivo alterado em '{caminho_resolvido}'."
    except Exception as e:
        return f"Erro ao alterar o arquivo: {str(e)}"


@mcp.tool()
def excluir_arquivo(caminho: str) -> str:
    """
    Exclui um arquivo local informado pelo utilizador.
    Ação destrutiva: só deve ser executada por pedido expresso do utilizador.

    Args:
        caminho (str): Caminho completo do arquivo a ser excluído.

    Returns:
        str: Mensagem de sucesso ou erro.
    """
    try:
        caminho_resolvido = _resolver_caminho(caminho)
        if not caminho_resolvido.exists() or not caminho_resolvido.is_file():
            return f"Erro: O arquivo '{caminho}' não foi encontrado."
        if _verificar_caminho_sensivel(caminho_resolvido):
            return f"Erro: Operação bloqueada. O caminho '{caminho}' aponta para uma área sensível do sistema."
        os.remove(caminho_resolvido)
        return f"Sucesso: Arquivo excluído '{caminho_resolvido}'."
    except Exception as e:
        return f"Erro ao excluir o arquivo: {str(e)}"


if __name__ == "__main__":
    print("[INFO] Local Filesystem MCP Server ativo.", file=sys.stderr)
    mcp.run()