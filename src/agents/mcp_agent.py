import asyncio
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Inicializa variáveis de ambiente do sistema.
load_dotenv()

async def run_mcp_agent():
    """
    Orquestra a conexão local entre o modelo de linguagem e o Servidor MCP.
    """
    # 1. Configuração dos parâmetros do processo servidor.
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_servers/math_server.py"]
    )

    print("🔌 Iniciando conexão com o Servidor MCP local via stdio...")
    
    # Inicialização do cliente MCP via stdio com gerenciamento de contexto para encerramento seguro.
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicialização da sessão.
            await session.initialize()
            
            # 2. Mapeamento das ferramentas (Skills) disponíveis no servidor.
            mcp_tools_response = await session.list_tools()
            ferramentas = [tool.name for tool in mcp_tools_response.tools]
            print(f"🛠️  Skills MCP carregadas com sucesso: {ferramentas}")
            
            # 3. Validação de execução de ação local via MCP.
            print("\n⚙️  Executando ação local 'add_numbers' (10.5 + 4.2) via MCP...")
            resultado_mcp = await session.call_tool(
                "add_numbers", 
                arguments={"first_number": 10.5, "second_number": 4.2}
            )
            
            # Extração do resultado do bloco de conteúdo retornado.
            print(f"✅ Resultado retornado pelo ambiente local: {resultado_mcp.content[0].text}")
            
            # 4. Ponto de integração para roteamento dinâmico via OpenRouter (Módulo A).

if __name__ == "__main__":
    # Ponto de entrada da execução assíncrona.
    asyncio.run(run_mcp_agent())