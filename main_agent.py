"""
Main Agent Orchestrator - Runs the self-improving scraper for n iterations
"""
import asyncio
import os
from typing import Dict, Any, List
from claude_agent_sdk import query, ClaudeAgentOptions
from tools import create_mcp_server
import config


async def run_iteration(iteration_num: int, amazon_url: str, expected_fields: List[str]) -> Dict[str, Any]:
    """
    Run a single iteration of the scraping loop.
    
    Args:
        iteration_num: Current iteration number (1-indexed)
        amazon_url: URL of Amazon product page to scrape
        expected_fields: List of fields to extract
        
    Returns:
        Dictionary with iteration results
    """
    print(f"\n{'='*60}")
    print(f"ITERATION {iteration_num}")
    print(f"{'='*60}\n")
    
    # Create MCP server with custom tools
    mcp_server = create_mcp_server()
    
    # Configure agent options
    options = ClaudeAgentOptions(
        mcp_servers={"scraper-tools": mcp_server},
        setting_sources=["project"],  # Load .claude/CLAUDE.md
        model="claude-3-5-sonnet-20241022"
    )
    
    # Build prompt for this iteration
    prompt = f"""
You are running iteration {iteration_num} of {config.NUM_ITERATIONS} iterations.

Target URL: {amazon_url}
Expected Fields: {', '.join(expected_fields)}

Your task:
1. THINK: Analyze the HTML structure using the HTML Analyzer subagent
2. BUILD: Generate scraping strategies using the Scraper Builder subagent
3. ACT: Execute strategies to extract data using fetch_html and parse_html_with_selectors tools
4. EVAL: Evaluate results using the Evaluator subagent and calculate metrics
5. FEEDBACK: Store results using store_iteration_result tool

If this is not iteration 1, review previous iterations using get_previous_iterations tool to learn from past attempts.

Execute the full think→build→act→eval→feedback cycle autonomously.
Report your results, including:
- Strategies tried
- Best strategy selected
- Success rate
- Metrics (completeness, quality, etc.)
"""
    
    try:
        # Query the agent
        result = query(prompt, options=options)
        
        # Collect all messages
        messages = []
        async for message in result:
            messages.append(message)
            print(message)
        
        return {
            "iteration": iteration_num,
            "messages": messages,
            "status": "completed"
        }
    except Exception as e:
        print(f"Error in iteration {iteration_num}: {str(e)}")
        return {
            "iteration": iteration_num,
            "error": str(e),
            "status": "failed"
        }


async def main():
    """Main entry point - runs n iterations and selects best scraper."""
    print("="*60)
    print("Self-Improving Amazon Scraper")
    print("="*60)
    print(f"Target URL: {config.AMAZON_URL}")
    print(f"Iterations: {config.NUM_ITERATIONS}")
    print(f"Fields to extract: {', '.join(config.FIELDS_TO_EXTRACT)}")
    print("="*60)
    
    # Verify API key is set
    if not config.ANTHROPIC_API_KEY:
        print("ERROR: ANTHROPIC_API_KEY environment variable not set!")
        return
    
    # Run iterations
    iteration_results = []
    for i in range(1, config.NUM_ITERATIONS + 1):
        result = await run_iteration(i, config.AMAZON_URL, config.FIELDS_TO_EXTRACT)
        iteration_results.append(result)
        
        # Small delay between iterations
        if i < config.NUM_ITERATIONS:
            await asyncio.sleep(2)
    
    # Summary
    print(f"\n{'='*60}")
    print("ITERATION SUMMARY")
    print(f"{'='*60}\n")
    
    # Load best scraper from patterns.json
    try:
        import json
        if os.path.exists(config.PATTERNS_FILE):
            with open(config.PATTERNS_FILE, "r") as f:
                patterns = json.load(f)
                best_scraper = patterns.get("best_scraper")
                if best_scraper:
                    print(f"Best Scraper (Iteration {best_scraper.get('iteration')}):")
                    print(f"  Success Rate: {best_scraper.get('success_rate', 0):.2%}")
                    print(f"  Strategy: {json.dumps(best_scraper.get('strategy', {}), indent=2)}")
    except Exception as e:
        print(f"Error loading best scraper: {str(e)}")
    
    print(f"\nAll results stored in {config.PATTERNS_FILE}")


if __name__ == "__main__":
    asyncio.run(main())

