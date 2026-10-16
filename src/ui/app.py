import asyncio
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import threading
from typing import Generator
import streamlit as st

# Garante o diretório raiz no PYTHONPATH
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.mcp_agent import MCPAgent

# Diretório de Persistência Local
CONVERSATIONS_DIR = PROJECT_ROOT / "data" / "conversations"
CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------
# Funções de Gerenciamento de Persistência (JSON)
# ----------------------------------------------------------------------
def list_conversations() -> list[dict]:
    """Lê todas as conversas salvas em disco, ordenadas pela mais recente."""
    files = sorted(CONVERSATIONS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)
    conversations = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                conversations.append(data)
        except Exception:
            continue
    return conversations


def save_conversation(conv_id: str, title: str, ui_messages: list, agent_messages: list) -> None:
    """Salva o estado visual e o contexto do LLM em arquivo JSON."""
    filepath = CONVERSATIONS_DIR / f"{conv_id}.json"
    
    # Converte os objetos internos da OpenAI (se existirem) em dicionários simples para o JSON
    serializable_agent_messages = []
    for msg in agent_messages:
        if hasattr(msg, "model_dump"):
            serializable_agent_messages.append(msg.model_dump(exclude_none=True))
        else:
            serializable_agent_messages.append(msg)
            
    data = {
        "id": conv_id,
        "title": title,
        "updated_at": datetime.now().isoformat(),
        "ui_messages": ui_messages,
        "agent_messages": serializable_agent_messages,
    }
    with open(filepath, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)


def load_conversation(conv_id: str) -> dict | None:
    """Carrega os dados de uma conversa específica."""
    filepath = CONVERSATIONS_DIR / f"{conv_id}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as fp:
            return json.load(fp)
    return None


def delete_conversation(conv_id: str) -> None:
    """Exclui fisicamente o arquivo da conversa."""
    filepath = CONVERSATIONS_DIR / f"{conv_id}.json"
    if filepath.exists():
        filepath.unlink()


# ----------------------------------------------------------------------
# Ponte Assíncrona MCP (AsyncBridge)
# ----------------------------------------------------------------------
class AsyncBridge:
    def __init__(self) -> None:
        if os.name == "nt":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self) -> None:
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    def stream_turn(self, agent: MCPAgent, user_input: str) -> Generator[tuple[str, str], None, None]:
        queue: asyncio.Queue = asyncio.Queue()

        async def _producer():
            try:
                async for event_type, payload in agent.process_turn(user_input):
                    await queue.put((event_type, payload))
            except Exception as e:
                await queue.put(("error", str(e)))
            finally:
                await queue.put((None, None))

        asyncio.run_coroutine_threadsafe(_producer(), self.loop)

        while True:
            future = asyncio.run_coroutine_threadsafe(queue.get(), self.loop)
            event_type, payload = future.result()
            if event_type is None:
                break
            yield event_type, payload


# ----------------------------------------------------------------------
# Configuração e Inicialização de Estado da Aplicação
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="LLMinds — Assistente Modular",
    page_icon="🤖",
    layout="wide",
)

if "bridge" not in st.session_state:
    st.session_state.bridge = AsyncBridge()

if "agent" not in st.session_state:
    with st.spinner("Inicializando ecossistema MCP e conectando servidores..."):
        agent = MCPAgent()
        st.session_state.bridge.run(agent.initialize())
        st.session_state.agent = agent

# Inicialização da Sessão Ativa
if "current_conv_id" not in st.session_state:
    all_convs = list_conversations()
    if all_convs:
        latest = all_convs[0]
        st.session_state.current_conv_id = latest["id"]
        st.session_state.current_title = latest.get("title", "Nova conversa")
        st.session_state.messages = latest.get("ui_messages", [])
        if "agent_messages" in latest and latest["agent_messages"]:
            st.session_state.agent.messages = latest["agent_messages"]
    else:
        new_id = f"conv_{int(datetime.now().timestamp())}"
        st.session_state.current_conv_id = new_id
        st.session_state.current_title = "Nova conversa"
        st.session_state.messages = []
        save_conversation(new_id, "Nova conversa", [], st.session_state.agent.messages)

if "messages" not in st.session_state:
    st.session_state.messages = []


# ----------------------------------------------------------------------
# Barra Lateral: Gestão de Conversas (Estilo Gemini)
# ----------------------------------------------------------------------
with st.sidebar:
    st.title("🤖 LLMinds")

    if st.button("➕ Nova conversa", use_container_width=True, type="primary"):
        new_id = f"conv_{int(datetime.now().timestamp())}"
        st.session_state.current_conv_id = new_id
        st.session_state.current_title = "Nova conversa"
        st.session_state.messages = []
        # Mantém apenas o prompt de sistema no agente
        if len(st.session_state.agent.messages) > 0:
            st.session_state.agent.messages = [st.session_state.agent.messages[0]]
        save_conversation(new_id, "Nova conversa", [], st.session_state.agent.messages)
        st.rerun()

    st.markdown("### 💬 Conversas")
    conversations = list_conversations()

    for conv in conversations:
        c_id = conv["id"]
        c_title = conv.get("title", "Sem título")
        is_active = c_id == st.session_state.current_conv_id

        col_btn, col_menu = st.columns([0.80, 0.20])

        with col_btn:
            label = f"▸ {c_title}" if is_active else c_title
            if st.button(label, key=f"btn_{c_id}", use_container_width=True):
                if not is_active:
                    st.session_state.current_conv_id = c_id
                    st.session_state.current_title = c_title
                    st.session_state.messages = conv.get("ui_messages", [])
                    if "agent_messages" in conv and conv["agent_messages"]:
                        st.session_state.agent.messages = conv["agent_messages"]
                    st.rerun()

        with col_menu:
            with st.popover("⋮", use_container_width=True):
                st.caption(f"Gerenciar: {c_title[:18]}")
                new_name = st.text_input("Novo título:", value=c_title, key=f"name_{c_id}")
                if st.button("✏️ Renomear", key=f"save_name_{c_id}", use_container_width=True):
                    conv_data = load_conversation(c_id)
                    if conv_data:
                        conv_data["title"] = new_name
                        with open(CONVERSATIONS_DIR / f"{c_id}.json", "w", encoding="utf-8") as fp:
                            json.dump(conv_data, fp, ensure_ascii=False, indent=2)
                        if is_active:
                            st.session_state.current_title = new_name
                        st.rerun()

                st.divider()
                if st.button("🗑️ Excluir", key=f"del_{c_id}", type="secondary", use_container_width=True):
                    delete_conversation(c_id)
                    if is_active:
                        remaining = list_conversations()
                        if remaining:
                            nxt = remaining[0]
                            st.session_state.current_conv_id = nxt["id"]
                            st.session_state.current_title = nxt.get("title", "Nova conversa")
                            st.session_state.messages = nxt.get("ui_messages", [])
                            if "agent_messages" in nxt and nxt["agent_messages"]:
                                st.session_state.agent.messages = nxt["agent_messages"]
                        else:
                            fresh_id = f"conv_{int(datetime.now().timestamp())}"
                            st.session_state.current_conv_id = fresh_id
                            st.session_state.current_title = "Nova conversa"
                            st.session_state.messages = []
                            if len(st.session_state.agent.messages) > 0:
                                st.session_state.agent.messages = [st.session_state.agent.messages[0]]
                            save_conversation(fresh_id, "Nova conversa", [], st.session_state.agent.messages)
                    st.rerun()

    st.divider()

    # Seção de Configurações Técnicas
    st.markdown("### ⚙️ Configurações do Agente")
    available_models = [
        "openai/gpt-4o-mini",
        "nvidia/nemotron-3.5-lightning:free",
        "nvidia/nemotron-3.5-super-vl:free",
        "google/gemma-4-31b-it:free",
        "anthropic/claude-opus-5.5"
    ]

    selected_model = st.selectbox(
        "Modelo (OpenRouter):",
        options=available_models,
        index=0,
    )
    st.session_state.agent.model_name = selected_model

    st.divider()
    st.markdown("### 🔌 Servidores MCP")
    st.success("✓ `math_server.py`")
    st.success("✓ `rag_server.py`")


# ----------------------------------------------------------------------
# Área Principal de Chat
# ----------------------------------------------------------------------
st.title(f"💬 {st.session_state.current_title}")
st.caption(f"ID da Sessão: `{st.session_state.current_conv_id}` | Modelo: `{selected_model}`")

# Renderização do Histórico Persistido
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tools" in msg and msg["tools"]:
            with st.expander("Ferramentas acionadas", expanded=False):
                for tool in msg["tools"]:
                    st.code(tool, language="text")

# Envio de Novas Mensagens
if prompt := st.chat_input("Digite sua mensagem..."):
    # Atualiza o título da conversa automaticamente a partir da primeira pergunta
    if st.session_state.current_title == "Nova conversa":
        resumo = prompt.strip().replace("\n", " ")
        st.session_state.current_title = resumo[:32] + "..." if len(resumo) > 35 else resumo

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_container = st.status("Processando requisição...", expanded=True)
        executed_tools = []
        final_answer = ""

        try:
            for event_type, payload in st.session_state.bridge.stream_turn(st.session_state.agent, prompt):
                if event_type == "tool_call":
                    status_container.write(f"⚡ **Chamada MCP:** `{payload}`")
                    executed_tools.append(f"Chamada: {payload}")
                elif event_type == "tool_result":
                    preview = payload.splitlines()[0] if payload else "Sem retorno"
                    status_container.write(f"✓ **Retorno:** {preview[:80]}...")
                    executed_tools.append(f"Resultado:\n{payload}")
                elif event_type == "assistant_response":
                    final_answer = payload
                elif event_type == "error":
                    status_container.error(f"Erro: {payload}")

            status_container.update(label="Concluído!", state="complete", expanded=False)
            st.markdown(final_answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": final_answer,
                "tools": executed_tools,
            })

            # Salva o estado completo no disco após cada turno
            save_conversation(
                st.session_state.current_conv_id,
                st.session_state.current_title,
                st.session_state.messages,
                st.session_state.agent.messages,
            )

        except Exception as e:
            status_container.update(label="Erro no processamento", state="error", expanded=True)
            st.error(f"Falha operacional: {str(e)}")