# Quick Start Guide

## Prerequisites

1. Python 3.8 or higher
2. Claude API key from [Claude Console](https://console.anthropic.com/)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set API Key

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Or on Windows:
```cmd
set ANTHROPIC_API_KEY=your-api-key-here
```

### 3. (Optional) Configure Settings

Edit `config.py` to change:
- `NUM_ITERATIONS`: Number of iterations (default: 3)
- `AMAZON_URL`: Target Amazon product page URL
- `FIELDS_TO_EXTRACT`: Fields to extract

Or use environment variables:
```bash
export NUM_ITERATIONS=5
export AMAZON_URL="https://www.amazon.com/dp/YOUR_PRODUCT_ID"
```

### 4. Run the Agent

```bash
python main_agent.py
```

The agent will:
- Run n iterations autonomously
- Learn and improve with each iteration
- Store results in `patterns.json`
- Display best scraper at the end

### 5. View Results

- Check `patterns.json` for detailed results
- Open `ui/index.html` in a browser for dashboard (note: currently shows simulated data)

## Testing Tools

Test custom tools independently:

```bash
python test_tools.py
```

## Troubleshooting

### API Key Not Set
```
ERROR: ANTHROPIC_API_KEY environment variable not set!
```
**Solution**: Set the environment variable as shown in step 2.

### Import Errors
If you get import errors for `claude_agent_sdk`:
```bash
pip install --upgrade claude-agent-sdk
```

### SDK API Differences
The Claude Agent SDK API may vary. If you encounter issues:

1. Check the [official documentation](https://docs.claude.com/en/docs/agent-sdk/overview)
2. Verify the SDK version: `pip show claude-agent-sdk`
3. Adjust imports in `main_agent.py` and `tools/__init__.py` if needed

Common adjustments might be needed for:
- `query()` function signature
- `ClaudeAgentOptions` parameters
- `@tool` decorator format
- `create_sdk_mcp_server()` parameters

## Expected Output

```
============================================================
Self-Improving Amazon Scraper
============================================================
Target URL: https://www.amazon.com/dp/B08N5WRWNW
Iterations: 3
Fields to extract: product_name, price, description, ratings, reviews
============================================================

============================================================
ITERATION 1
============================================================

[Agent executes think→build→act→eval→feedback cycle]

============================================================
ITERATION SUMMARY
============================================================

Best Scraper (Iteration 3):
  Success Rate: 92.00%
  Strategy: {...}

All results stored in patterns.json
```

## Next Steps

- Review `patterns.json` to see learned patterns
- Check iteration results and improvements
- Modify subagents in `.claude/agents/` to customize behavior
- Adjust tools in `tools/` directory to add new capabilities

