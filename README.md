# Self-Improving Amazon Scraper

An autonomous AI agent built with Claude Agent SDK that scrapes Amazon.com product pages and continuously improves its scraping strategies through iterative learning - all without manual intervention.

## 🎯 Core Concept

The agent runs **n fixed iterations** (default: 3) on the same Amazon product page, autonomously learning and improving with each cycle following the **think → build → act → eval → feedback → think again** loop.

## 🏗️ Architecture

### Main Agent
- Orchestrates the self-improving loop
- Manages n iterations
- Coordinates subagents
- Selects best scraper at the end

### Subagents
1. **HTML Analyzer**: Analyzes HTML structure and suggests CSS selectors
2. **Scraper Builder**: Generates and refines scraping strategies
3. **Evaluator**: Assesses data quality and success metrics

### Custom MCP Tools
- `fetch_html`: Fetch HTML content from URLs
- `parse_html_with_selectors`: Extract data using CSS selectors
- `store_iteration_result`: Store iteration results
- `get_previous_iterations`: Retrieve past results
- `get_best_scraper`: Get best scraper found
- `store_site_pattern`: Store learned patterns
- `get_site_pattern`: Retrieve learned patterns
- `calculate_completeness`: Calculate data completeness
- `calculate_quality_score`: Calculate quality score
- `compare_iterations`: Compare metrics between iterations

## 📋 Prerequisites

- Python 3.8+
- Claude API key from [Claude Console](https://console.anthropic.com/)

## 🚀 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variable:**
   ```bash
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```

3. **Configure (optional):**
   Edit `config.py` to change:
   - Number of iterations (`NUM_ITERATIONS`)
   - Amazon product URL (`AMAZON_URL`)
   - Fields to extract (`FIELDS_TO_EXTRACT`)

## 💻 Usage

### Run the Agent

```bash
python main_agent.py
```

The agent will:
1. Run n iterations autonomously
2. Learn from each iteration
3. Improve scraping strategies
4. Select the best scraper at the end
5. Store results in `patterns.json`

### View Dashboard

Open `ui/index.html` in a web browser to see:
- Iteration progress
- Metrics over time
- Autonomous actions log
- Best scraper details

## 📊 Output

Results are stored in `patterns.json`:
- All iteration results
- Best scraper configuration
- Success rates and metrics
- Learned patterns

## 🔄 Iteration Flow

**Iteration 1:**
- Think: Analyze HTML structure (no prior knowledge)
- Build: Generate multiple scraping strategies
- Act: Execute strategies, extract data
- Eval: Measure completeness, quality, speed
- Feedback: Store best strategy, record metrics

**Iteration 2-N:**
- Think: Check learned patterns, detect changes
- Build: Refine strategies based on feedback
- Act: Execute optimized strategy
- Eval: Compare to previous iteration
- Feedback: Update success rates, refine patterns

## 🎯 Success Criteria

- ✅ Agent runs n iterations autonomously (no manual intervention)
- ✅ Success rate improves across iterations (measurable trend)
- ✅ Agent makes all decisions independently
- ✅ Clear visualization of improvement over iterations
- ✅ Works with real Amazon.com product pages
- ✅ Best scraper selected at end (highest success rate)

## 📁 Project Structure

```
/
├── main_agent.py              # Main orchestrator
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── patterns.json              # Learned patterns (auto-generated)
├── .claude/
│   ├── agents/
│   │   ├── html_analyzer.md   # HTML analysis subagent
│   │   ├── scraper_builder.md # Strategy building subagent
│   │   └── evaluator.md       # Evaluation subagent
│   └── CLAUDE.md              # Main agent system prompt
├── tools/                     # Custom MCP tools
│   ├── html_fetcher.py
│   ├── html_parser.py
│   ├── pattern_storage.py
│   ├── metrics_tracker.py
│   └── __init__.py
└── ui/                        # Dashboard UI
    ├── index.html
    ├── app.js
    └── styles.css
```

## 🛠️ Customization

### Change Number of Iterations

Set environment variable:
```bash
export NUM_ITERATIONS=5
```

Or edit `config.py`:
```python
NUM_ITERATIONS = 5
```

### Change Target URL

Set environment variable:
```bash
export AMAZON_URL="https://www.amazon.com/dp/YOUR_PRODUCT_ID"
```

Or edit `config.py`:
```python
AMAZON_URL = "https://www.amazon.com/dp/YOUR_PRODUCT_ID"
```

## 📝 Notes

- The agent respects website resources and uses appropriate delays
- All decisions are made autonomously without human input
- Patterns are learned and reused across iterations
- Best scraper is automatically selected based on success rate

## 🤝 Contributing

This is a hackathon project demonstrating self-improving AI agents with Claude Agent SDK.

## 📄 License

MIT License
