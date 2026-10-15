from mcp.server.mcpserver import MCPServer
import sys

# Inicializa o servidor MCP
mcp = MCPServer("Math_Server")

@mcp.tool()
def add_numbers(first_number: float, second_number: float) -> float:
    return first_number + second_number

@mcp.tool()
def multiply_numbers(first_factor: float, second_factor: float) -> float:
    return first_factor * second_factor

if __name__ == "__main__":
    # Redireciona o print para o stderr para não poluir o JSON-RPC do stdout
    print("Iniciando Math MCP Server via stdio...", file=sys.stderr)
    mcp.run()