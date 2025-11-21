import anyio
import os
import shutil
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import McpStdioServerConfig


def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def load_system_prompt():
    """Load system prompt from prompts/system.j2."""
    prompts_dir = Path(__file__).parent / "prompts"
    system_prompt_path = prompts_dir / "system.j2"
    with open(system_prompt_path, "r") as f:
        return f.read().strip()


def get_brave_api_key():
    """Get Brave API key from environment and warn if missing."""
    brave_api_key = os.environ.get("BRAVE_API_KEY", "")
    if not brave_api_key:
        print("Warning: BRAVE_API_KEY not found in environment")
    return brave_api_key


def configure_mcp_servers(brave_api_key):
    """Configure MCP servers for Brave Search and CoinGecko."""
    npx_path = shutil.which("npx") or "npx"
    
    mcp_servers = {}
    
    # Configure Brave Search
    brave_env = os.environ.copy()
    if brave_api_key:
        brave_env["BRAVE_API_KEY"] = brave_api_key
    mcp_servers["brave-search"] = McpStdioServerConfig(
        command=npx_path,
        args=["-y", "@modelcontextprotocol/server-brave-search"],
        env=brave_env
    )
    
    # Configure CoinGecko Remote Server (no API key required)
    mcp_servers["coingecko"] = McpStdioServerConfig(
        command=npx_path,
        args=["mcp-remote", "https://mcp.api.coingecko.com/sse"],
        env=os.environ.copy()
    )
    
    return mcp_servers


def create_agent_options(system_prompt, mcp_servers):
    """Create ClaudeAgentOptions with the given configuration."""
    return ClaudeAgentOptions(
        system_prompt=system_prompt,
        model="claude-haiku-4-5",
        mcp_servers=mcp_servers,
        permission_mode="bypassPermissions"
    )


async def query_agent(prompt, options):
    """Query the agent and collect messages."""
    messages = []
    async for message in query(prompt=prompt, options=options):
        messages.append(message)
    return messages


def extract_response(messages):
    """Extract the final response from ResultMessage."""
    for message in messages:
        if hasattr(message, 'subtype') and message.subtype == 'success':
            return message.result
    return None


async def main():
    load_env_file()
    system_prompt = load_system_prompt()
    brave_api_key = get_brave_api_key()
    mcp_servers = configure_mcp_servers(brave_api_key)
    options = create_agent_options(system_prompt, mcp_servers)

    print(f"MCP servers configured: {list(mcp_servers.keys())}")
    print(f"BRAVE_API_KEY set: {bool(brave_api_key)}")
    print(f"CoinGecko using remote server (no API key required)")

    messages = await query_agent(
        prompt="Hello! Can you get current price of BTC in USD?",
        options=options
    )

    return extract_response(messages)


if __name__ == "__main__":
    response = anyio.run(main)
    print("Response: ", response)