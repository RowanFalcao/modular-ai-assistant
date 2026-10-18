import asyncio
import os
import sys
from pathlib import Path

# Inclusão da raiz do projeto para suporte a execuções diretas
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.mcp_agent import MCPAgent
from src.agents.error_handler import format_api_error


def render_banner() -> None:
    """Exibe o cabeçalho padronizado da interface CLI."""
    border = "=" * 60
    print(border)
    print("        MODULAR AI ASSISTANT - SISTEMA MULTI-AGENTE")
    print("                 Arquitetura MVC & MCP Core")
    print(border)
    print("Comandos do sistema:")
    print("  'sair', 'exit' ou 'quit' : Finaliza a sessão ativa.")
    print("  'limpar' ou 'clear'      : Limpa o ecrã do terminal.")
    print("-" * 60)


async def main() -> None:
    """Entrypoint principal da aplicação: View e Controller unificados."""
    render_banner()
    agent = MCPAgent()

    print("[INFO] A inicializar conexões com os servidores MCP...")
    try:
        await agent.initialize()
        print("[SUCESSO] Ecossistema pronto para operação.\n")
    except Exception as e:
        print(f"[FALHA] Não foi possível carregar os servidores locais: {str(e)}")
        return

    while True:
        try:
            user_input = input("utilizador > ")
            
            # 1. Ignora imediatamente espaços vazios e enters acidentais sem acionar a API
            if not user_input.strip():
                continue

            # Remove espaços em branco residuais para análise de comandos
            cmd = user_input.strip().lower()

            if cmd in ["sair", "exit", "quit"]:
                print("\n[INFO] A terminar sessão do ecossistema...")
                break

            if cmd in ["limpar", "clear"]:
                os.system("cls" if os.name == "nt" else "clear")
                render_banner()
                continue

            # Processamento assíncrono com bloqueio seguro
            async for event_type, payload in agent.process_turn(user_input):
                if event_type == "tool_call":
                    print(f"  [⚡ Ação] A executar ferramenta externa: {payload}")
                elif event_type == "tool_result":
                    preview = payload.splitlines()[0] if payload else "Sem retorno"
                    print(f"  [✓ Concluído] Retorno obtido: {preview[:70]}...")
                elif event_type == "assistant_response":
                    print(f"\nassistente > {payload}\n")
                elif event_type in ("api_error", "error"):
                    err = format_api_error(payload)
                    print(f"\n[AVISO DO PROVEDOR] {err['title']}")
                    print(f"  Mensagem: {err['message']}")
                    print(f"  Sugestão: {err['action']}\n")

        except KeyboardInterrupt:
            print("\n\n[INFO] Sinal de interrupção (Ctrl+C) recebido. A encerrar de forma segura...")
            break
        except Exception as e:
            # Protege contra o print de erro vazio e indica onde falhou
            error_msg = str(e) if str(e).strip() else "Exceção desconhecida interceptada."
            print(f"\n[ERRO OPERACIONAL] Falha no processamento do agente: {error_msg}\n")

    await agent.shutdown()
    print("[INFO] Todos os servidores foram desligados com sucesso.")


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass