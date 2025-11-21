"""
Custom MCP tools for the self-improving scraper
"""
from claude_agent_sdk import create_sdk_mcp_server
from .html_fetcher import fetch_html
from .html_parser import parse_html_with_selectors
from .pattern_storage import (
    store_iteration_result,
    get_previous_iterations,
    get_best_scraper,
    store_site_pattern,
    get_site_pattern
)
from .metrics_tracker import (
    calculate_completeness,
    calculate_quality_score,
    compare_iterations
)


def create_mcp_server():
    """Create and return the MCP server with all custom tools."""
    return create_sdk_mcp_server(
        name="scraper-tools",
        version="1.0.0",
        tools=[
            fetch_html,
            parse_html_with_selectors,
            store_iteration_result,
            get_previous_iterations,
            get_best_scraper,
            store_site_pattern,
            get_site_pattern,
            calculate_completeness,
            calculate_quality_score,
            compare_iterations
        ]
    )

