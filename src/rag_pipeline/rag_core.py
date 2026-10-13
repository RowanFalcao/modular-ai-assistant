import os
from qdrant_client import QdrantClient
from llama_index.core import StorageContext, Settings, SimpleDirectoryReader, VectorStoreIndex
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.postprocessor import SentenceTransformerRerank

def get_vector_db_client():
    """
    Inicializa o cliente local do Qdrant para armazenamento vetorial.
    Os dados são salvos localmente na pasta data/vector_db para garantir a portabilidade.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "data", "vector_db")
    os.makedirs(db_path, exist_ok=True)
    
    client = QdrantClient(path=db_path)
    return client

def setup_rag_pipeline():
    """
    Configura o motor principal do RAG com o Qdrant e o modelo de embeddings local.
    """
    print("Configurando motor RAG...")
    
    # 1. Configurar o modelo de Embeddings (BGE-M3 local)
    print("Carregando modelo de embeddings (BAAI/bge-m3)...")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-m3")
    
    # Desativamos o LLM temporariamente apenas para esta etapa de configuração do motor de busca
    Settings.llm = None 
    
    # 2. Conectar o LlamaIndex ao nosso banco Qdrant
    qdrant_client = get_vector_db_client()
    vector_store = QdrantVectorStore(client=qdrant_client, collection_name="llminds_knowledge_base")
    
    # 3. Criar o contexto de armazenamento
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    print("Pipeline RAG (Qdrant + BGE-M3) configurado com sucesso!")
    return storage_context

if __name__ == "__main__":
    # Teste de execução direta do pipeline
    setup_rag_pipeline()