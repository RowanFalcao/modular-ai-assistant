import sys
from mcp.server.mcpserver import MCPServer

# 1. Inicializa o servidor com um nome claro
mcp = MCPServer("Template_Skill_Server")

# 2. Usa o decorator @mcp.tool() para expor a função
@mcp.tool()
def ferramenta_exemplo(parametro_texto: str, parametro_numero: int) -> str:
    """
    Ferramenta de exemplo (Placeholder).
    Utilize este arquivo como base para criar novas skills ou baixe skills prontas
    via script install_skill.py.
    
    Args:
        parametro_texto (str): O que a IA deve enviar aqui.
        parametro_numero (int): O que a IA deve enviar aqui.
        
    Returns:
        str: O resultado da operação ou mensagem de erro formatada.
    """
    try:
        resultado = parametro_texto * parametro_numero
        return f"Skill de exemplo executada com sucesso: {resultado}"
    except Exception as e:
        return f"Falha na execução: {str(e)}"

if __name__ == "__main__":
    # 3. Log de inicialização sempre no stderr para não quebrar o IPC
    print("Iniciando Template Skill MCP Server...", file=sys.stderr)
    mcp.run()