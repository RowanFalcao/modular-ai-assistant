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
    Loop principal do Agente: Conecta o LLM (OpenRouter) às ferramentas locais (MCP).
    """
    # 1. Configura o Cérebro (Cliente OpenRouter)
    llm_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )
    
    # 2. Configura a Mão (Servidor MCP Local)
    server_params = StdioServerParameters(
        command="python",
        args=["src/mcp_servers/math_server.py"]
    )

    print("🔌 Conectando ao Servidor MCP local...")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. Lê as ferramentas locais e converte para o formato da OpenAI (Tool Calling)
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
            
            print(f"🛠️  Ferramentas enviadas para a IA: {[t.name for t in mcp_tools_response.tools]}")
            
            # 4. O Prompt do Usuário
            user_prompt = "Olá! Pode me dizer qual é o resultado de 1545 somado com 342?"
            print(f"\n👤 Usuário: {user_prompt}")
            
            messages = [{"role": "user", "content": user_prompt}]
            
            # 5. O Cérebro Pensa: Enviamos o prompt e as ferramentas para a IA
            print("🧠 IA está pensando...")
            response = await llm_client.chat.completions.create(
                model="openai/gpt-4o-mini", # Pode usar claude-3.5-sonnet se preferir
                messages=messages,
                tools=openai_tools,
                tool_choice="auto"
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            # 6. A Decisão: A IA decidiu usar alguma ferramenta?
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    print(f"⚡ IA decidiu usar a ferramenta local: {tool_call.function.name}")
                    
                    # Converte os argumentos que a IA enviou
                    tool_args = json.loads(tool_call.function.arguments)
                    print(f"📦 Argumentos recebidos da IA: {tool_args}")
                    
                    # 7. A Ação: Executa a ferramenta localmente no seu PC!
                    mcp_result = await session.call_tool(tool_call.function.name, arguments=tool_args)
                    result_text = mcp_result.content[0].text
                    print(f"✅ Resultado local gerado: {result_text}")
                    
                    # 8. Devolvemos o resultado para o Cérebro
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text
                    })
                
                # 9. A Resposta Final: A IA formula a frase final com o resultado em mãos
                print("🧠 IA formulando a resposta final...")
                final_response = await llm_client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=messages
                )
                print(f"\n🤖 Assistente: {final_response.choices[0].message.content}")
            else:
                # Se a IA achar que não precisa de ferramentas, ela só responde normalmente
                print(f"\n🤖 Assistente: {response_message.content}")

if __name__ == "__main__":
    asyncio.run(run_mcp_agent())