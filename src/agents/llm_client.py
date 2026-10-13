import os
from dotenv import load_dotenv
from openai import OpenAI

# Carrega as variáveis de ambiente definidas no arquivo .env
load_dotenv()

def get_openrouter_client() -> OpenAI:
    """Inicializa e retorna o cliente da API do OpenRouter."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "sk-or-v1-sua_chave_real_aqui":
        raise ValueError("OPENROUTER_API_KEY válida não encontrada no arquivo .env!")

    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def test_inference() -> str:
    """Executa um teste básico de chamada ao modelo de linguagem."""
    client = get_openrouter_client()
    
    response = client.chat.completions.create(
        model="nvidia/nemotron-3.5-lightning:free",
        messages=[
            {"role": "user", "content": "Olá! Responda em uma única frase: qual é a sua principal função?"}
        ]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    print("Enviando requisição para o OpenRouter...")
    resposta = test_inference()
    print("\n[Resposta da IA]:", resposta)