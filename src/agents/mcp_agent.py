import asyncio
import json
import os
import sys
from contextlib import AsyncExitStack
from typing import AsyncGenerator
from dotenv import load_dotenv
from openai import AsyncOpenAI
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

load_dotenv()


class MCPAgent:
    """
    Model de execução e raciocínio lógico do ecossistema.
    Gere o ciclo de vida de múltiplos servidores MCP, o estado conversacional
    e as chamadas determinísticas de inferência via LLM.
    """

    def __init__(self, model_name: str = "openai/gpt-4o-mini") -> None:
        self.model_name = model_name
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY"),
        )
        self.server_configs = [
            StdioServerParameters(
                command=sys.executable,
                args=["src/mcp_servers/math_server.py"],
            ),
            StdioServerParameters(
                command=sys.executable,
                args=["src/mcp_servers/rag_server.py"],
            ),
        ]
        self.exit_stack = AsyncExitStack()
        self.sessions: dict[str, ClientSession] = {}
        self.openai_tools: list[dict] = []
        self.api_tools: list[dict] = []
        self.messages: list[dict] = [
            {
                "role": "system",
                "content": (
                    "Você é o Orquestrador Principal do sistema modular. "
                    "Utilize as ferramentas disponíveis para resolução de problemas matemáticos "
                    "e consulta à base privada de documentos antes de formular respostas definitivas."
                ),
            }
        ]

    async def initialize(self) -> None:
        """Inicializa as conexões IPC com os servidores MCP registados."""
        for params in self.server_configs:
            server_name = os.path.basename(params.args[0])

            read, write = await self.exit_stack.enter_async_context(stdio_client(params))
            session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            self.sessions[server_name] = session

            mcp_tools_response = await session.list_tools()
            for tool in mcp_tools_response.tools:
                self.openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.input_schema,
                    },
                    "_server_owner": server_name,
                })

        self.api_tools = [
            {"type": t["type"], "function": t["function"]}
            for t in self.openai_tools
        ]

    async def process_turn(self, user_input: str) -> AsyncGenerator[tuple[str, str], None]:
        """
        Executa uma iteração de conversação.
        Emite eventos de estado (tipo, carga) para a camada de apresentação.
        """
        self.messages.append({"role": "user", "content": user_input})

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages,
            tools=self.api_tools,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        self.messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                tool_name = tool_call.function.name
                yield ("tool_call", tool_name)

                owner_server = next(
                    (t["_server_owner"] for t in self.openai_tools if t["function"]["name"] == tool_name),
                    None,
                )

                if owner_server:
                    tool_args = json.loads(tool_call.function.arguments)
                    mcp_result = await self.sessions[owner_server].call_tool(
                        tool_name,
                        arguments=tool_args,
                    )
                    result_text = mcp_result.content[0].text

                    yield ("tool_result", result_text)

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    })
                else:
                    yield ("error", f"Servidor não localizado para {tool_name}")

            final_response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=self.messages,
            )
            final_text = final_response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": final_text})
            yield ("assistant_response", final_text)

        else:
            yield ("assistant_response", response_message.content)

    async def shutdown(self) -> None:
        """Encerra com segurança todas as sessões e canais de subprocessos."""
        await self.exit_stack.aclose()