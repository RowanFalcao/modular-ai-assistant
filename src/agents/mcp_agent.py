import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


# Carregamento de variáveis de ambiente locais
load_dotenv()


async def run_mcp_agent() -> None:
    """
    Orquestrador de execução para múltiplos servidores MCP.
    Gerencia conexões assíncronas, roteamento dinâmico de ferramentas e o loop de diálogo.
    """
    llm_client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    # Registro declarativo dos servidores MCP locais utilizando o interpretador do ambiente ativo
    server_configs = [
        StdioServerParameters(command=sys.executable, args=["src/mcp_servers/math_server.py"]),
        StdioServerParameters(command=sys.executable, args=["src/mcp_servers/rag_server.py"]),
    ]

    print("Conectando aos servidores MCP locais...")

    # Gerenciamento concorrente de múltiplos contextos assíncronos
    async with AsyncExitStack() as stack:
        sessions = {}
        openai_tools = []

        for params in server_configs:
            server_name = os.path.basename(params.args[0])

            read, write = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            sessions[server_name] = session

            # Conversão de esquemas de ferramentas MCP para compatibilidade com a API OpenAI
            mcp_tools_response = await session.list_tools()
            for tool in mcp_tools_response.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                    "_server_owner": server_name,
                })

        # Remoção de metadados internos antes da serialização para a API
        api_tools = [
            {"type": t["type"], "function": t["function"]}
            for t in openai_tools
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "Você é o Orquestrador Principal do sistema modular. "
                    "Utilize as ferramentas disponíveis para resolução de problemas matemáticos "
                    "e consulta à base privada de documentos antes de formular respostas definitivas."
                ),
            }
        ]

        print("Ecossistema MCP conectado com sucesso.")
        print("Digite 'sair' para encerrar a sessão.")
        print("-" * 50)

        # Loop interativo de interação com o usuário
        while True:
            user_prompt = input("\nUsuário: ")

            if user_prompt.strip().lower() in ["sair", "exit", "quit"]:
                print("Sessão encerrada.")
                break

            if not user_prompt.strip():
                continue

            messages.append({"role": "user", "content": user_prompt})

            try:
                # Inferência inicial para identificação de intenção e seleção de ferramentas
                response = await llm_client.chat.completions.create(
                    model="openai/gpt-4o-mini",
                    messages=messages,
                    tools=api_tools,
                    tool_choice="auto",
                )

                response_message = response.choices[0].message
                messages.append(response_message)

                # Processamento de chamadas de ferramentas locais
                if response_message.tool_calls:
                    for tool_call in response_message.tool_calls:
                        tool_name = tool_call.function.name
                        print(f"-> Executando ferramenta: {tool_name}")

                        # Resolução de rota para o servidor proprietário da ferramenta
                        owner_server = next(
                            (t["_server_owner"] for t in openai_tools if t["function"]["name"] == tool_name),
                            None,
                        )

                        if owner_server:
                            tool_args = json.loads(tool_call.function.arguments)
                            mcp_result = await sessions[owner_server].call_tool(
                                tool_name,
                                arguments=tool_args,
                            )
                            result_text = mcp_result.content[0].text
                            # Log técnico de observabilidade para depuração local
                            print(f"<- Retorno da ferramenta [{tool_name}]: {result_text}")
                            
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": result_text,
                            })
                        else:
                            print(f"Erro: Servidor não mapeado para a ferramenta {tool_name}")

                    # Inferência secundária para síntese final integrando o resultado das ações
                    final_response = await llm_client.chat.completions.create(
                        model="openai/gpt-4o-mini",
                        messages=messages,
                    )
                    final_text = final_response.choices[0].message.content

                    messages.append({"role": "assistant", "content": final_text})
                    print(f"\nAssistente: {final_text}")

                else:
                    print(f"\nAssistente: {response_message.content}")

            except Exception as e:
                print(f"Erro durante a execução do ciclo de interação: {str(e)}")


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(run_mcp_agent())