import anyio
import argparse
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import McpStdioServerConfig
import anthropic


def setup_logging_directory():
    """Create logs directory if it doesn't exist."""
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir


def create_log_file(logs_dir, coin_name):
    """Create a timestamped log file for this session."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"agent_log_{coin_name}_{timestamp}.jsonl"
    return logs_dir / log_filename


def log_message(log_file, message_type, data):
    """Log a message to the log file in JSONL format."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "type": message_type,
        "data": data
    }
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")


def serialize_message(message):
    """Convert a message object to a serializable dictionary."""
    try:
        # Try to get all attributes of the message
        data = {}
        if hasattr(message, "__dict__"):
            for key, value in message.__dict__.items():
                try:
                    json.dumps(value)  # Test if serializable
                    data[key] = value
                except (TypeError, ValueError):
                    # If not directly serializable, convert to string
                    data[key] = str(value)
        else:
            data = {"message": str(message)}
        
        # Add type information
        data["_message_type"] = type(message).__name__
        
        # Check for specific attributes that indicate tool calls or MCP usage
        if hasattr(message, "tool_calls") or hasattr(message, "tool_call"):
            data["_has_tool_call"] = True
        if hasattr(message, "mcp") or hasattr(message, "server"):
            data["_has_mcp"] = True
            
        return data
    except Exception as e:
        return {"error": f"Failed to serialize message: {str(e)}", "raw": str(message)}


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


async def query_agent(prompt, options, log_file=None):
    """Query the agent and collect messages, logging each step."""
    messages = []
    
    # Log the initial prompt
    if log_file:
        log_message(log_file, "user_prompt", {"prompt": prompt})
    
    async for message in query(prompt=prompt, options=options):
        messages.append(message)
        
        # Log each message
        if log_file:
            message_data = serialize_message(message)
            
            # Determine message type for better categorization
            message_type = "agent_message"
            if hasattr(message, "tool_calls") or hasattr(message, "tool_call"):
                message_type = "tool_call"
            elif hasattr(message, "subtype"):
                if message.subtype == "success":
                    message_type = "result_success"
                elif message.subtype == "error":
                    message_type = "result_error"
            
            log_message(log_file, message_type, message_data)
            
            # Also log to console for visibility
            # print(f"[LOG] {message_type}: {type(message).__name__}")
    
    return messages


def extract_response(messages):
    """Extract the final response from ResultMessage."""
    for message in messages:
        if hasattr(message, 'subtype') and message.subtype == 'success':
            return message.result
    return None


def extract_structured_decision(response_text, log_file=None):
    """Extract structured decision (BUY/SELL) and reason from response using Claude structured outputs."""
    if not response_text:
        return None
    
    # Get Anthropic API key from environment
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not found in environment")
        return None
    
    client = anthropic.Anthropic(api_key=api_key)
    
    try:
        response = client.beta.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            betas=["structured-outputs-2025-11-13"],
            messages=[
                {
                    "role": "user",
                    "content": f"Extract the decision (BUY or SELL) and reason from this crypto research report:\n\n{response_text}"
                }
            ],
            output_format={
                "type": "json_schema",
                "schema": {
                    "type": "object",
                    "properties": {
                        "decision": {
                            "type": "string",
                            "enum": ["BUY", "SELL"]
                        },
                        "reason": {
                            "type": "string"
                        }
                    },
                    "required": ["decision", "reason"],
                    "additionalProperties": False
                }
            }
        )
        
        structured_output = json.loads(response.content[0].text)
        
        # Log the structured extraction
        if log_file:
            log_message(log_file, "structured_extraction", {
                "original_response": response_text,
                "structured_output": structured_output
            })
        
        return structured_output
        
    except Exception as e:
        error_msg = f"Failed to extract structured decision: {str(e)}"
        print(f"Error: {error_msg}")
        if log_file:
            log_message(log_file, "structured_extraction_error", {
                "error": error_msg,
                "original_response": response_text
            })
        return None


async def main(coin_name):
    load_env_file()
    
    # Set up logging
    logs_dir = setup_logging_directory()
    log_file = create_log_file(logs_dir, coin_name)
    print(f"Logging to: {log_file}")
    
    system_prompt = load_system_prompt()
    brave_api_key = get_brave_api_key()
    mcp_servers = configure_mcp_servers(brave_api_key)
    options = create_agent_options(system_prompt, mcp_servers)

    # Log initial configuration
    log_message(log_file, "session_start", {
        "coin_name": coin_name,
        "mcp_servers": list(mcp_servers.keys()),
        "brave_api_key_set": bool(brave_api_key),
        "model": options.model if hasattr(options, "model") else "unknown",
        "system_prompt_length": len(system_prompt)
    })
    
    # Log MCP server details
    mcp_details = {}
    for server_name, server_config in mcp_servers.items():
        mcp_details[server_name] = {
            "command": server_config.command if hasattr(server_config, "command") else None,
            "args": server_config.args if hasattr(server_config, "args") else None,
        }
    log_message(log_file, "mcp_configuration", mcp_details)

    print(f"MCP servers configured: {list(mcp_servers.keys())}")
    print(f"BRAVE_API_KEY set: {bool(brave_api_key)}")
    print(f"CoinGecko using remote server (no API key required)")
    print(f"Researching coin: {coin_name}")

    prompt = f"\n\nCoin name: {coin_name}"
    
    messages = await query_agent(
        prompt=prompt,
        options=options,
        log_file=log_file
    )
    
    # Extract raw response
    raw_response = extract_response(messages)
    
    # Extract structured decision
    structured_decision = None
    if raw_response:
        structured_decision = extract_structured_decision(raw_response, log_file)
    
    # Log session end
    log_message(log_file, "session_end", {
        "total_messages": len(messages),
        "response_extracted": raw_response is not None,
        "structured_decision_extracted": structured_decision is not None
    })

    return {
        "raw_response": raw_response,
        "structured_decision": structured_decision
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crypto research agent")
    parser.add_argument("--coin-name", required=True, help="Coin name to research (e.g., BTC, ETH)")
    args = parser.parse_args()
    
    result = anyio.run(main, args.coin_name)
    
    if result:
        print("\n" + "="*50)
        print("RESPONSE SUMMARY")
        print("="*50)
        
        if result.get("structured_decision"):
            decision = result["structured_decision"]
            print(f"\nDecision: {decision.get('decision', 'N/A')}")
            print(f"Reason: {decision.get('reason', 'N/A')}")
        else:
            print("\nStructured decision extraction failed or unavailable.")
    