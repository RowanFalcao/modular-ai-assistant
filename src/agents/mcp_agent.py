import asyncio
import os
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Inicializa variáveis de ambiente
load_dotenv()

async def run_mcp_agent():
    """
    Loop principal do Agente com memória de curto prazo e chat interativo.
    """
    llm_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_servers/math_server.py"]
    )

    print("🔌 Conectando ao Servidor MCP local...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 1. Converte ferramentas do MCP para o padrão OpenAI
            mcp_tools_response = await session.list_tools()
            openai_tools = []
            
            for tool in mcp_tools_response.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or f"Executa a ferramenta {tool.name}",
                        "parameters": tool.input_schema
                    }
                })
            
            # 2. Inicializa a "Memória" do Agente (Histórico de Conversa)
            # O system prompt dita o comportamento geral da IA.
            messages = [
                {
                    "role": "system", 
                    "content": "Você é um assistente de IA prestativo e analítico. Use as ferramentas fornecidas para cálculos matemáticos precisos."
                }
            ]
            
            print("✅ Agente pronto! Digite 'sair' para encerrar o chat.")
            print("-" * 50)
            
            # 3. O Loop Interativo de Chat
            while True:
                user_prompt = input("\n👤 Você: ")
                
                # Condição de saída graciosa
                if user_prompt.strip().lower() in ['sair', 'exit', 'quit']:
                    print("👋 Encerrando o assistente. Até logo!")
                    break
                
                # Se o usuário apertar Enter sem digitar nada, apenas ignora
                if not user_prompt.strip():
                    continue
                    
                # Anota a nova mensagem do usuário na memória
                messages.append({"role": "user", "content": user_prompt})
                
                try:
                    # Envia todo o histórico para o Cérebro
                    response = await llm_client.chat.completions.create(
                        model="openai/gpt-4o-mini", # Pode alterar para claude-3.5-sonnet se quiser
                        messages=messages,
                        tools=openai_tools,
                        tool_choice="auto"
                    )
                    
                    response_message = response.choices[0].message
                    # Anota a resposta (ou a decisão de usar a ferramenta) na memória
                    messages.append(response_message)
                    
                    # 4. Tratamento de Tool Calling (Ação Local)
                    if response_message.tool_calls:
                        for tool_call in response_message.tool_calls:
                            print(f"   [⚡ IA executando: {tool_call.function.name}]")
                            
                            tool_args = json.loads(tool_call.function.arguments)
                            mcp_result = await session.call_tool(tool_call.function.name, arguments=tool_args)
                            result_text = mcp_result.content[0].text
                            
                            # Anota o resultado da ferramenta na memória para o Cérebro ler
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_text
                            })
                        
                        # O Cérebro lê o resultado da ferramenta e formula a resposta final
                        final_response = await llm_client.chat.completions.create(
                            model="openai/gpt-4o-mini",
                            messages=messages
                        )
                        final_text = final_response.choices[0].message.content
                        
                        # Anota a resposta final na memória e exibe na tela
                        messages.append({"role": "assistant", "content": final_text})
                        print(f"🤖 Assistente: {final_text}")
                    
                    else:
                        # Resposta direta (sem ferramentas)
                        print(f"🤖 Assistente: {response_message.content}")
                        
                except Exception as e:
                    print(f"❌ Erro de comunicação com a IA: {str(e)}")

if __name__ == "__main__":
    # Silencia possíveis avisos não críticos do Windows no terminal
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(run_mcp_agent())