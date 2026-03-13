from infrastructure.config import load_config
from infrastructure.mcp import create_mcp

mcp = create_mcp()

if __name__ == "__main__":
    config = load_config()
    mcp.run(transport="sse", host=config.mcp.host, port=config.mcp.port)

