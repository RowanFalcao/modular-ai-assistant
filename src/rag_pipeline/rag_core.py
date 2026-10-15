import os
from pathlib import Path
from qdrant_client import QdrantClient
from llama_index.core import (
    StorageContext,
    Settings,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.postprocessor import SentenceTransformerRerank

COLLECTION_NAME = "llminds_knowledge_base"


def get_base_dir() -> Path:
    """Retorna o caminho absoluto do diretório raiz do projeto."""
    return Path(__file__).resolve().parent.parent.parent


def get_vector_db_client() -> QdrantClient:
    """
    Inicializa o cliente local do Qdrant para armazenamento vetorial.
    Os dados são salvos localmente na pasta data/vector_db para garantir a portabilidade.
    """
    db_path = get_base_dir() / "data" / "vector_db"
    db_path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(db_path))


def configure_pipeline_settings() -> None:
    """Configura o modelo de embeddings BGE-M3 local e desativa LLM no LlamaIndex."""
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
    Settings.llm = None


def setup_rag_pipeline() -> StorageContext:
    """
    Configura o motor principal do RAG com o Qdrant e o modelo de embeddings local.
    """
    configure_pipeline_settings()
    qdrant_client = get_vector_db_client()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return storage_context


def ingest_documents(raw_data_dir: str = "data/raw") -> None:
    """
    Varre a pasta de dados brutos, gera os embeddings vetoriais e persiste no Qdrant.
    """
    configure_pipeline_settings()
    raw_path = get_base_dir() / raw_data_dir

    if not raw_path.exists():
        raw_path.mkdir(parents=True, exist_ok=True)
        print(f"Diretório {raw_data_dir} criado. Nenhum documento indexado.")
        return

    # Leitura ignorando arquivos ocultos como .gitkeep
    reader = SimpleDirectoryReader(
        input_dir=str(raw_path),
        recursive=False,
        required_exts=[".txt", ".pdf", ".md"],
    )
    documents = reader.load_data()

    if not documents:
        print("Nenhum arquivo elegível (.txt, .pdf, .md) encontrado em data/raw.")
        return

    print(f"Indexando {len(documents)} documento(s) na coleção '{COLLECTION_NAME}'...")

    qdrant_client = get_vector_db_client()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Persistência atômica no Qdrant
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
    )
    print("Indexação de documentos concluída com sucesso.")


if __name__ == "__main__":
    # Permite executar a ingestão diretamente via CLI
    ingest_documents()