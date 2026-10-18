"""
Módulo de Tratamento Resiliente e Amigável de Erros de API.
Converte falhas de upstream do OpenRouter e chamadas de rede em orientações claras para o usuário.
"""
from typing import Any, Dict


def format_api_error(error: Any) -> Dict[str, str]:
    """
    Analisa a exceção ou mensagem de erro retornada pela API e devolve
    uma estrutura limpa, amigável e acionável para a interface do usuário.
    """
    error_str = str(error)
    error_lower = error_str.lower()

    # 1. Rate Limit / Cota Temporária Excedida (HTTP 429)
    if "429" in error_str or "rate-limited" in error_lower or "rate_limit" in error_lower or "too many requests" in error_lower:
        return {
            "title": "Limite Temporário de Requisições do Modelo",
            "message": "O provedor deste modelo gratuito está temporariamente com alto volume de acessos na fila compartilhada global.",
            "action": "Alterne na barra lateral esquerda para outro modelo gratuito (como 'nvidia/nemotron-3.5-lightning:free') ou aguarde cerca de 1 a 2 minutos para tentar novamente.",
            "raw": error_str,
            "badge": "warning"
        }

    # 2. Falta de Crédito / Saldo Insuficiente (HTTP 402)
    if "402" in error_str or "insufficient_quota" in error_lower or "insufficient balance" in error_lower or "credits" in error_lower:
        return {
            "title": "Saldo Insuficiente na Conta",
            "message": "O modelo selecionado é proprietário (pago) e a sua conta no OpenRouter não possui saldo de créditos suficiente.",
            "action": "Selecione um modelo com o sufixo ':free' (como 'nvidia/nemotron-3.5-lightning:free' ou 'google/gemma-4-31b-it:free') na barra lateral para continuar sem custos, ou recarregue créditos na plataforma.",
            "raw": error_str,
            "badge": "error"
        }

    # 3. Chave de API Inválida ou Não Autorizada (HTTP 401)
    if "401" in error_str or "authenticationerror" in error_lower or "unauthorized" in error_lower or "invalid_api_key" in error_lower:
        return {
            "title": "Chave de API Não Autorizada",
            "message": "A chave OPENROUTER_API_KEY informada no arquivo .env parece inválida, expirou ou não possui autorização.",
            "action": "Abra o arquivo .env na raiz do projeto e certifique-se de que a sua chave do OpenRouter foi inserida corretamente.",
            "raw": error_str,
            "badge": "error"
        }

    # 4. Limite de Contexto Excedido (HTTP 400 / Token Limit)
    if "context_length_exceeded" in error_lower or "maximum context length" in error_lower or "too many tokens" in error_lower:
        return {
            "title": "Limite de Contexto Atingido",
            "message": "O volume acumulado de mensagens e documentos desta sessão ultrapassou a janela máxima de memória suportada por este modelo.",
            "action": "Clique em '➕ Nova conversa' na barra lateral para iniciar uma sessão nova e limpa.",
            "raw": error_str,
            "badge": "info"
        }

    # 5. Instabilidade / Falha no Servidor Upstream (HTTP 500, 502, 503, 504)
    if any(code in error_str for code in ["500", "502", "503", "504"]) or "bad gateway" in error_lower or "service unavailable" in error_lower or "internal server error" in error_lower:
        return {
            "title": "Servidor do Provedor Temporariamente Indisponível",
            "message": "Os servidores do provedor responsável por este modelo específico estão enfrentando instabilidade momentânea.",
            "action": "Alterne temporariamente para outro modelo na barra lateral enquanto o provedor restabelece a estabilidade.",
            "raw": error_str,
            "badge": "warning"
        }

    # 6. Timeout ou Queda de Conexão de Rede
    if "timeout" in error_lower or "connectionerror" in error_lower or "connecterror" in error_lower or "timed out" in error_lower:
        return {
            "title": "Falha de Conexão com o Provedor",
            "message": "Não foi possível estabelecer contato com a API de inferência dentro do tempo limite.",
            "action": "Verifique a sua conexão com a internet e tente enviar a mensagem novamente.",
            "raw": error_str,
            "badge": "warning"
        }

    # 7. Fallback para Erros Não Mapeados
    return {
        "title": "Falha Operacional no Modelo",
        "message": "O provedor do modelo não pôde concluir o processamento desta solicitação.",
        "action": "Tente reenviar a mensagem ou alternar para outro modelo na barra lateral.",
        "raw": error_str,
        "badge": "error"
    }
