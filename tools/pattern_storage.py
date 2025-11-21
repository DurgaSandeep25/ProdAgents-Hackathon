"""
Pattern Storage Tool - Custom MCP tool for storing and retrieving learned patterns
"""
import json
import os
from typing import Dict, Any
from datetime import datetime
from claude_agent_sdk import tool


PATTERNS_FILE = "patterns.json"


def _load_patterns() -> Dict[str, Any]:
    """Load patterns from JSON file."""
    if os.path.exists(PATTERNS_FILE):
        try:
            with open(PATTERNS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "iterations": [],
        "best_scraper": None,
        "site_patterns": {}
    }


def _save_patterns(patterns: Dict[str, Any]) -> None:
    """Save patterns to JSON file."""
    with open(PATTERNS_FILE, "w") as f:
        json.dump(patterns, f, indent=2)


@tool(
    "store_iteration_result",
    "Store the results of an iteration including strategies tried, best strategy, and success metrics.",
    {
        "iteration": {
            "type": "number",
            "description": "Iteration number (1-indexed)"
        },
        "strategies_tried": {
            "type": "array",
            "description": "List of strategies that were tried in this iteration"
        },
        "best_strategy": {
            "type": "object",
            "description": "The best strategy from this iteration with selectors and metadata"
        },
        "success_rate": {
            "type": "number",
            "description": "Success rate (0.0 to 1.0) for this iteration"
        },
        "metrics": {
            "type": "object",
            "description": "Additional metrics (completeness, quality, speed, etc.)"
        }
    }
)
async def store_iteration_result(args: Dict[str, Any]) -> Dict[str, Any]:
    """Store iteration results in patterns.json."""
    patterns = _load_patterns()
    
    iteration_data = {
        "iteration": args.get("iteration"),
        "strategies_tried": args.get("strategies_tried", []),
        "best_strategy": args.get("best_strategy", {}),
        "success_rate": args.get("success_rate", 0.0),
        "metrics": args.get("metrics", {}),
        "timestamp": datetime.now().isoformat()
    }
    
    patterns["iterations"].append(iteration_data)
    
    # Update best scraper if this iteration has higher success rate
    current_best = patterns.get("best_scraper")
    if not current_best or iteration_data["success_rate"] > current_best.get("success_rate", 0.0):
        patterns["best_scraper"] = {
            "iteration": iteration_data["iteration"],
            "strategy": iteration_data["best_strategy"],
            "success_rate": iteration_data["success_rate"]
        }
    
    _save_patterns(patterns)
    
    return {
        "content": [{
            "type": "text",
            "text": f"Iteration {iteration_data['iteration']} results stored successfully. Success rate: {iteration_data['success_rate']:.2%}"
        }]
    }


@tool(
    "get_previous_iterations",
    "Retrieve all previous iteration results to learn from past attempts.",
    {}
)
async def get_previous_iterations(args: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve all previous iteration results."""
    patterns = _load_patterns()
    iterations = patterns.get("iterations", [])
    
    import json
    return {
        "content": [{
            "type": "text",
            "text": json.dumps(iterations, indent=2)
        }]
    }


@tool(
    "get_best_scraper",
    "Retrieve the best scraper configuration found so far.",
    {}
)
async def get_best_scraper(args: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve the best scraper configuration."""
    patterns = _load_patterns()
    best_scraper = patterns.get("best_scraper")
    
    import json
    if best_scraper:
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(best_scraper, indent=2)
            }]
        }
    else:
        return {
            "content": [{
                "type": "text",
                "text": "No best scraper found yet."
            }]
        }


@tool(
    "store_site_pattern",
    "Store learned patterns for a specific site/domain.",
    {
        "domain": {
            "type": "string",
            "description": "The domain name (e.g., 'amazon.com')"
        },
        "selectors": {
            "type": "object",
            "description": "Dictionary mapping field names to CSS selectors"
        },
        "success_rate": {
            "type": "number",
            "description": "Success rate for this pattern (0.0 to 1.0)"
        }
    }
)
async def store_site_pattern(args: Dict[str, Any]) -> Dict[str, Any]:
    """Store learned patterns for a specific site."""
    patterns = _load_patterns()
    
    if "site_patterns" not in patterns:
        patterns["site_patterns"] = {}
    
    domain = args.get("domain")
    patterns["site_patterns"][domain] = {
        "selectors": args.get("selectors", {}),
        "success_rate": args.get("success_rate", 0.0),
        "last_updated": datetime.now().isoformat()
    }
    
    _save_patterns(patterns)
    
    return {
        "content": [{
            "type": "text",
            "text": f"Site pattern stored for {domain} with success rate {args.get('success_rate', 0.0):.2%}"
        }]
    }


@tool(
    "get_site_pattern",
    "Retrieve learned patterns for a specific site/domain.",
    {
        "domain": {
            "type": "string",
            "description": "The domain name (e.g., 'amazon.com')"
        }
    }
)
async def get_site_pattern(args: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve learned patterns for a specific site."""
    patterns = _load_patterns()
    domain = args.get("domain")
    
    site_patterns = patterns.get("site_patterns", {})
    if domain in site_patterns:
        import json
        return {
            "content": [{
                "type": "text",
                "text": json.dumps(site_patterns[domain], indent=2)
            }]
        }
    else:
        return {
            "content": [{
                "type": "text",
                "text": f"No pattern found for {domain}"
            }]
        }

