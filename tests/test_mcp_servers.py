import pytest
from src.mcp_servers.math_server import add_numbers, multiply_numbers
from src.mcp_servers.skill_server import ferramenta_exemplo
from src.mcp_servers.filesystem_server import _validate_path, ALLOWED_WORKSPACE


def test_math_server_add():
    assert add_numbers(2.5, 3.5) == 6.0
    assert add_numbers(-10.0, 5.0) == -5.0


def test_math_server_multiply():
    assert multiply_numbers(4.0, 2.5) == 10.0
    assert multiply_numbers(0.0, 100.0) == 0.0


def test_skill_server_exemplo():
    resultado = ferramenta_exemplo("A", 3)
    assert "AAA" in resultado


def test_filesystem_server_sandbox_seguro():
    # Caminho dentro do workspace permitido
    caminho_valido = ALLOWED_WORKSPACE / "README.md"
    validado = _validate_path(str(caminho_valido))
    assert validado == caminho_valido.resolve()

    # Caminho fora do workspace (diretorio pai) deve disparar PermissionError em qualquer SO
    caminho_fora = ALLOWED_WORKSPACE.parent / "arquivo_fora_do_workspace.txt"
    with pytest.raises(PermissionError):
        _validate_path(str(caminho_fora))
