from src.agents.mcp_agent import parse_xml_tool_calls, MCPAgent


def test_get_default_system_message():
    msg = MCPAgent.get_default_system_message()
    assert msg["role"] == "system"
    assert "listar_arquivos" in msg["content"]
    assert "ler_arquivo" in msg["content"]
    assert "salvar_arquivo" in msg["content"]


def test_parse_xml_tool_calls():
    xml_text = (
        "<tool_call>\n"
        "<function=listar_arquivos>\n"
        "<parameter=caminho>C:/Users/User/Desktop</parameter>\n"
        "</function>\n"
        "</tool_call>"
    )
    calls = parse_xml_tool_calls(xml_text)
    assert len(calls) == 1
    assert calls[0].function.name == "listar_arquivos"
    assert "C:/Users/User/Desktop" in calls[0].function.arguments

