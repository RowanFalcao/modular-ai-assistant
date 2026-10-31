import os
from pathlib import Path
import pytest
from src.mcp_servers.local_filesystem_server import (
    _resolver_caminho,
    _verificar_caminho_sensivel,
    listar_arquivos,
    ler_arquivo,
    salvar_arquivo,
    alterar_arquivo,
    excluir_arquivo,
)


def test_resolver_caminho_expande_caminho_absoluto(tmp_path: Path):
    caminho_resolvido = _resolver_caminho(str(tmp_path))
    assert caminho_resolvido.is_absolute()
    assert caminho_resolvido == tmp_path.resolve()


def test_verificar_caminho_sensivel():
    assert _verificar_caminho_sensivel(Path("C:/Windows/System32/cmd.exe")) is True
    assert _verificar_caminho_sensivel(Path("C:/Windows")) is True
    assert _verificar_caminho_sensivel(Path("/etc/passwd")) is True
    assert _verificar_caminho_sensivel(Path("C:/Users/User/Desktop/documento.txt")) is False


def test_listar_arquivos_diretorio_inexistente():
    resultado = listar_arquivos("caminho_que_certamente_nao_existe_12345")
    assert "Erro: O diretório" in resultado


def test_fluxo_completo_arquivos(tmp_path: Path):
    arquivo_teste = tmp_path / "teste_unitario.txt"
    conteudo_inicial = "conteudo inicial de teste"
    conteudo_atualizado = "conteudo atualizado de teste"

    # 1. Salvar arquivo
    res_salvar = salvar_arquivo(str(arquivo_teste), conteudo_inicial)
    assert "Sucesso" in res_salvar
    assert arquivo_teste.exists()

    # 2. Ler arquivo
    res_ler = ler_arquivo(str(arquivo_teste))
    assert res_ler == conteudo_inicial

    # 3. Listar arquivos
    res_listar = listar_arquivos(str(tmp_path))
    assert "teste_unitario.txt" in res_listar

    # 4. Alterar arquivo
    res_alterar = alterar_arquivo(str(arquivo_teste), conteudo_atualizado)
    assert "Sucesso" in res_alterar
    assert ler_arquivo(str(arquivo_teste)) == conteudo_atualizado

    # 5. Excluir arquivo
    res_excluir = excluir_arquivo(str(arquivo_teste))
    assert "Sucesso" in res_excluir
    assert not arquivo_teste.exists()


def test_bloqueio_caminho_sensivel():
    res_salvar = salvar_arquivo("C:/Windows/System32/hacked.txt", "teste")
    assert "Operação bloqueada" in res_salvar

    res_alterar = alterar_arquivo("C:/Windows/System32/hacked.txt", "teste")
    assert "não foi encontrado" in res_alterar or "Operação bloqueada" in res_alterar
