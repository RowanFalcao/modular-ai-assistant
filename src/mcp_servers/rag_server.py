import contextlib
import sys
from pathlib import Path

# Inclusão da raiz do repositório no sys.path para resolução de módulos internos
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from llama_index.core import VectorStoreIndex
from mcp.server.mcpserver import MCPServer
from src.rag_pipeline.rag_core import setup_rag_pipeline

# Inicialização da instância do servidor MCP
mcp = MCPServer("RAG_Server")

# Cache em memória da estrutura vetorial para evitar reinicializações
_rag_index = None


def _get_or_create_index() -> VectorStoreIndex:
    """
    Carrega o motor vetorial sob demanda.
    Redireciona emissões de log para stderr a fim de manter intacto o canal stdio.
    """
    global _rag_index
    if _rag_index is None:
        with contextlib.redirect_stdout(sys.stderr):
            storage_context = setup_rag_pipeline()
            _rag_index = VectorStoreIndex.from_vector_store(
                vector_store=storage_context.vector_store
            )
    return _rag_index


@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """
    Consulta a base local de documentos e editais indexados.
    Deve ser utilizada para responder sobre projetos, editais, regulamentações
    e informações corporativas ou acadêmicas internas.
    """
    try:
        index = _get_or_create_index()
    except ValueError as e:
         return "Erro ao carregar o banco vetorial local. Certifique-se de que a coleção existe no Qdrant."

    retriever = index.as_retriever(similarity_top_k=3)
    nodes = retriever.retrieve(query)

    if not nodes:
        return "Nenhum registro relevante encontrado para a consulta informada."

    context_text = "\n\n--- Fragmento de Documento ---\n\n".join(
        node.node.get_content() for node in nodes
    )

    return f"Resultados da consulta para '{query}':\n\n{context_text}"


if __name__ == "__main__":
    # Mensagens de ciclo de vida emitidas exclusivamente em stderr
    print("Iniciando RAG MCP Server via stdio...", file=sys.stderr)
    mcp.run()