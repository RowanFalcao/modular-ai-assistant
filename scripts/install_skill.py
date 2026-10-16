import sys
import urllib.request
from pathlib import Path

def main() -> None:
    """
    Ponto de entrada do script instalador de skills.
    Captura a URL do repositório remoto, baixa o arquivo de forma segura
    e posiciona no diretório arquitetural correto do ecossistema MCP.
    """
    print("=" * 60)
    print("     LLMINDS - INSTALADOR DE SKILLS DE TERCEIROS (MCP)")
    print("=" * 60)
    
    url = input("URL raw do script Python da Skill (ex: GitHub Raw): ").strip()
    if not url:
        print("[ERRO] URL não fornecida. Operação abortada.", file=sys.stderr)
        sys.exit(1)
        
    skill_name = input("Nome descritivo da Skill (ex: github, email, notion): ").strip().lower()
    if not skill_name:
        print("[ERRO] Nome não fornecido. Operação abortada.", file=sys.stderr)
        sys.exit(1)
        
    # Resolução de caminhos relativos para garantir portabilidade absoluta (Deploy Anywhere)
    project_root = Path(__file__).resolve().parent.parent
    dest_dir = project_root / "src" / "mcp_servers"
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = f"{skill_name}_server.py"
    dest_path = dest_dir / file_name
    
    print(f"\n[INFO] Iniciando download da skill...")
    print(f"[INFO] Origem: {url}")
    print(f"[INFO] Destino local: {dest_path}")
    
    try:
        # Download do código fonte em tempo de execução
        urllib.request.urlretrieve(url, dest_path)
        print(f"\n[SUCESSO] Skill '{skill_name}' instalada com sucesso no ecossistema!")
        print("\n[AÇÕES DE GOVERNANÇA EXIGIDAS]:")
        print("1. Abra o arquivo baixado e valide os imports no cabeçalho.")
        print("2. Se houver dependências externas, instale-as estritamente via: poetry add <pacote>")
        print(f"3. Registre o servidor no arquivo 'src/agents/mcp_agent.py' apontando para 'src/mcp_servers/{file_name}'.")
    except Exception as e:
        print(f"\n[ERRO OPERACIONAL] Falha ao processar o download: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()