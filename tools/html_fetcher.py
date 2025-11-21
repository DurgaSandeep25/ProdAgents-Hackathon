"""
HTML Fetcher Tool - Custom MCP tool for fetching HTML content from URLs
"""
import requests
from typing import Dict, Any
from claude_agent_sdk import tool


@tool(
    "fetch_html",
    "Fetch HTML content from a given URL. Returns the raw HTML as a string.",
    {
        "url": {
            "type": "string",
            "description": "The URL to fetch HTML from"
        }
    }
)
async def fetch_html(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch HTML content from a URL using requests library.
    
    Args:
        args: Dictionary containing 'url' key
        
    Returns:
        Dictionary with 'content' containing the HTML string
    """
    url = args.get("url")
    if not url:
        return {
            "content": [{
                "type": "text",
                "text": "Error: URL is required"
            }]
        }
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return {
            "content": [{
                "type": "text",
                "text": f"HTML fetched successfully. Length: {len(response.text)} characters.\n\n{response.text[:5000]}..." if len(response.text) > 5000 else response.text
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error fetching HTML: {str(e)}"
            }]
        }

