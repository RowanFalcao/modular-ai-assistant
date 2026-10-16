# 🛠️ Guia: Criação de Skills MCP (Model Context Protocol)

Este documento estabelece o padrão de engenharia do repositório `modular-ai-assistant` para a criação de novos Servidores MCP locais. Qualquer nova skill deve seguir estritamente este contrato para garantir que o Agente LLM compreenda e execute as ferramentas sem falhas de orquestração.

## 1. Regra de Ouro: Comunicação IPC (stdio)
Nossos servidores comunicam-se com o Orquestrador (`mcp_agent.py`) através de entradas e saídas padrão (`stdio`).
- **PROIBIDO:** Usar `print()` normal para depuração ou logs. Isso corrompe o JSON de comunicação entre o servidor e o orquestrador.
- **OBRIGATÓRIO:** Qualquer log ou mensagem no console DEVE ser redirecionado para o `sys.stderr`.
  - *Exemplo correto:* `print("Log de erro", file=sys.stderr)`

## 2. Tipagem Semântica e Docstrings (Clean Code para IAs)
O modelo de linguagem lê os metadados do seu código Python para saber como usar a ferramenta. 
- Use **Nomes de Variáveis Descritivos** (ex: `caminho_do_arquivo` em vez de `c`).
- Use **Type Hints** obrigatórios (`str`, `int`, `float`, `list`).
- Use **Docstrings** detalhadas na função, explicando *o que faz*, *quando usar* e *o que retorna*.

## 3. Template Base de um Servidor MCP
Salve os novos servidores sempre na pasta `src/mcp_servers/`. Use o template abaixo:

```python
import sys
from mcp.server.mcpserver import MCPServer

# 1. Inicializa o servidor com um nome claro
mcp = MCPServer("NomeDaSuaSkill_Server")

# 2. Usa o decorator @mcp.tool() para expor a função
@mcp.tool()
def sua_nova_ferramenta(parametro_texto: str, parametro_numero: int) -> str:
    """
    Docstring OBRIGATÓRIA.
    Descreva aqui de forma detalhada o que a ferramenta faz. A IA lerá este texto
    para decidir se deve ou não acionar esta skill durante a conversa.
    
    Args:
        parametro_texto (str): O que a IA deve enviar aqui.
        parametro_numero (int): O que a IA deve enviar aqui.
        
    Returns:
        str: O resultado da operação ou mensagem de erro formatada.
    """
    try:
        # Lógica da sua ferramenta aqui
        resultado = parametro_texto * parametro_numero
        return f"Sucesso: {resultado}"
    except Exception as e:
        # Retorne o erro em formato de string para a IA saber o que deu errado
        return f"Falha na execução: {str(e)}"

if __name__ == "__main__":
    # 3. Log de inicialização sempre no stderr
    print("Iniciando NomeDaSuaSkill MCP Server...", file=sys.stderr)
    # 4. Executa o servidor
    mcp.run()