import asyncio
import json
import os
import sys
import re
from contextlib import AsyncExitStack
from typing import Any, AsyncGenerator, cast
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

load_dotenv()

def parse_xml_tool_calls(text: str) -> list:
    """
    Adapter: Inspeciona texto bruto e cria uma classe anônima MockToolCall 
    que engana perfeitamente a biblioteca AsyncOpenAI.
    """
    import re
    import json
    
    class MockFunction:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments
            
    class MockToolCall:
        def __init__(self, id, type, function):
            self.id = id
            self.type = type
            self.function = function
            
    tool_calls = []
    pattern = re.compile(r"<tool_call>\s*<function=(?P<name>[^\s>]+)>(?P<args>.*?)</function>\s*</tool_call>", re.DOTALL)
    
    for i, m in enumerate(pattern.finditer(text)):
        func_name = m.group("name").strip()
        args_block = m.group("args")
        
        params = {}
        for pm in re.finditer(r"<parameter=(?P<pname>[^\s>]+)>(?P<pval>.*?)</parameter>", args_block, re.DOTALL):
            params[pm.group("pname").strip()] = pm.group("pval").strip()
            
        # Retorna o objeto exatamente como o loop do agent espera (usando notação de ponto .name e .arguments)
        mock_function = MockFunction(name=func_name, arguments=json.dumps(params, ensure_ascii=False))
        mock_call = MockToolCall(id=f"call_adapter_{i}", type="function", function=mock_function)
        tool_calls.append(mock_call)
        
    return tool_calls

class MCPAgent:
    """
    Model de execução e raciocínio lógico do ecossistema.
    Gere o ciclo de vida de múltiplos servidores MCP, o estado conversacional
    e as chamadas determinísticas de inferência via LLM.
    """

    @classmethod
    def get_default_system_message(cls) -> dict:
        return {
            "role": "system",
            "content": (
                "Você é o Orquestrador Principal de um sistema modular de engenharia de software.\n"
                "DIRETRIZES RÍGIDAS DE TOOL CALLING (USO DE FERRAMENTAS):\n"
                "1. Você tem acesso a ferramentas locais para manipular arquivos, matemática e buscas.\n"
                "2. Você DEVE acionar as ferramentas usando ESTRITAMENTE o formato nativo de Function Calling (JSON).\n"
                "3. É ESTRITAMENTE PROIBIDO escrever tags XML ou texto bruto como `<tool_call>`, `<function>` ou `<parameter>` na sua resposta de texto.\n"
                "4. Se você precisar executar múltiplas ferramentas (ex: listar diretório e depois escrever arquivo), faça UMA chamada de ferramenta, aguarde o resultado (tool_result), e só então faça a próxima chamada.\n"
                "5. Pense passo a passo, mas nunca exponha a sintaxe da ferramenta no texto.\n\n"
                "FERRAMENTAS DE ACESSO AO SISTEMA DE ARQUIVOS LOCAL DO UTILIZADOR:\n"
                "Você possui ferramentas que acessam QUALQUER pasta ou arquivo no computador local do utilizador (Desktop, Documentos, Downloads, etc.).\n"
                "- `listar_arquivos(caminho)` — Lista arquivos e pastas de um diretório local. Exemplo: listar_arquivos('C:\\\\Users\\\\User\\\\Desktop')\n"
                "- `ler_arquivo(caminho)` — Lê o conteúdo de um arquivo local.\n"
                "- `salvar_arquivo(caminho, conteudo)` — Cria ou sobrescreve um arquivo local.\n"
                "- `alterar_arquivo(caminho, conteudo)` — Altera um arquivo existente.\n"
                "- `excluir_arquivo(caminho)` — Exclui um arquivo (só por pedido explícito do utilizador).\n"
                "Quando o utilizador pedir para acessar, ler, listar ou manipular arquivos do computador dele, USE estas ferramentas.\n"
                "Aceite caminhos absolutos (C:\\\\...), relativos, e com ~ (diretório do utilizador)."
            ),
        }

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
            StdioServerParameters(
                command=sys.executable,
                args=["src/mcp_servers/filesystem_server.py"],
            ),
            StdioServerParameters(
                command=sys.executable,
                args=["src/mcp_servers/skill_server.py"],
            ),
            StdioServerParameters(
                command=sys.executable,
                args=["src/mcp_servers/local_filesystem_server.py"],
            ),
        ]
        self.exit_stack = AsyncExitStack()
        self.sessions = {}
        self.openai_tools = []
        self.api_tools = []
        self.messages: list[ChatCompletionMessageParam | Any] = [self.get_default_system_message()]

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

    async def _create_chat_completion(
        self,
        messages: list[Any],
        tools: list[dict] | None = None,
    ) -> ChatCompletion:
        """Centraliza e isola as chamadas à API, garantindo estritamente o tipo ChatCompletion."""
        kwargs: dict[str, Any] = {
            "model": self.model_name,
            "messages": cast(list[ChatCompletionMessageParam], messages),
        }
        if tools:
            kwargs["tools"] = cast(Any, tools)
            kwargs["tool_choice"] = "auto"

        res = await self.client.chat.completions.create(**kwargs)
        return cast(ChatCompletion, res)

    async def process_turn(self, user_input: str) -> AsyncGenerator[tuple[str, str], None]:
        """
        Executa uma iteração de conversação.
        Emite eventos de estado (tipo, carga) para a camada de apresentação.
        """
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = await self._create_chat_completion(self.messages, self.api_tools)
        except Exception as e:
            if self.messages and isinstance(self.messages[-1], dict) and self.messages[-1].get("role") == "user":
                self.messages.pop()
            yield ("api_error", str(e))
            return

        response_message = response.choices[0].message

        # INTERCEPTAÇÃO: Adapter de Formato (Fallback)
        if response_message.content and "<tool_call>" in response_message.content:
            parsed_tools = parse_xml_tool_calls(response_message.content)
            if parsed_tools:
                response_message.tool_calls = parsed_tools
                response_message.content = None

        self.messages.append(response_message)

        if response_message.tool_calls:
            for tool_call in response_message.tool_calls:
                func = getattr(tool_call, "function", None)
                if func is None:
                    continue

                tool_name = getattr(func, "name", "")
                yield ("tool_call", tool_name)

                owner_server = next(
                    (t["_server_owner"] for t in self.openai_tools if t["function"]["name"] == tool_name),
                    None,
                )

                if owner_server:
                    tool_args = json.loads(getattr(func, "arguments", "{}"))
                    mcp_result = await self.sessions[owner_server].call_tool(
                        tool_name,
                        arguments=tool_args,
                    )
                    result_text = mcp_result.content[0].text if mcp_result.content else ""

                    yield ("tool_result", result_text)

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    })
                else:
                    yield ("error", f"Servidor não localizado para {tool_name}")

            try:
                final_response = await self._create_chat_completion(self.messages)
                final_text = final_response.choices[0].message.content or ""
                self.messages.append({"role": "assistant", "content": final_text})
                yield ("assistant_response", final_text)
            except Exception as e:
                yield ("api_error", str(e))
                return

        else:
            yield ("assistant_response", response_message.content or "")

    async def shutdown(self) -> None:
        """Encerra com segurança todas as sessões e canais de subprocessos."""
        await self.exit_stack.aclose()
