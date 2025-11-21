"""
HTML Parser Tool - Custom MCP tool for parsing HTML and extracting data using CSS selectors
"""
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from claude_agent_sdk import tool


@tool(
    "parse_html_with_selectors",
    "Parse HTML content and extract data using CSS selectors. Returns extracted data as JSON.",
    {
        "html": {
            "type": "string",
            "description": "The HTML content to parse"
        },
        "selectors": {
            "type": "object",
            "description": "Dictionary mapping field names to CSS selectors (e.g., {'product_name': 'h1#productTitle', 'price': '.a-price-whole'})"
        }
    }
)
async def parse_html_with_selectors(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse HTML and extract data using CSS selectors.
    
    Args:
        args: Dictionary containing 'html' and 'selectors' keys
        
    Returns:
        Dictionary with extracted data
    """
    html = args.get("html", "")
    selectors = args.get("selectors", {})
    
    if not html:
        return {
            "content": [{
                "type": "text",
                "text": "Error: HTML content is required"
            }]
        }
    
    if not selectors:
        return {
            "content": [{
                "type": "text",
                "text": "Error: Selectors dictionary is required"
            }]
        }
    
    try:
        soup = BeautifulSoup(html, "lxml")
        extracted_data = {}
        
        for field_name, selector in selectors.items():
            try:
                elements = soup.select(selector)
                if elements:
                    # Extract text from all matching elements
                    values = [elem.get_text(strip=True) for elem in elements]
                    extracted_data[field_name] = values[0] if len(values) == 1 else values
                else:
                    extracted_data[field_name] = None
            except Exception as e:
                extracted_data[field_name] = f"Error: {str(e)}"
        
        import json
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(extracted_data, indent=2)
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text",
                "text": f"Error parsing HTML: {str(e)}"
            }]
        }

