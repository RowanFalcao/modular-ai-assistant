from src.agents.error_handler import format_api_error


def test_format_api_error_rate_limit_429():
    info = format_api_error("Error 429: rate_limit exceeded")
    assert info["badge"] == "warning"
    assert "Limite Temporário" in info["title"]
    assert "Alterne" in info["action"]


def test_format_api_error_insufficient_quota_402():
    info = format_api_error("Error 402: insufficient_quota")
    assert info["badge"] == "error"
    assert "Saldo Insuficiente" in info["title"]


def test_format_api_error_unauthorized_401():
    info = format_api_error("AuthenticationError: 401 Unauthorized")
    assert info["badge"] == "error"
    assert "Não Autorizada" in info["title"]


def test_format_api_error_fallback():
    info = format_api_error("Erro desconhecido e aleatorio")
    assert info["badge"] == "error"
    assert info["title"] == "Falha Operacional no Modelo"
