# Market Analysis v2 Implementation

This package implements the Market Analysis feature using **Agno v2 patterns** with Step objects and explicit Agent definitions, maintaining complete isolation from existing v1 code.

## Architecture Overview

### Hybrid v1/v2 Approach
- **Existing code (v1)**: Remains untouched in `agent/stock_analysis.py`
- **New code (v2)**: Implemented here using modern Agno patterns
- **Router**: Modified `agent/main.py` handles routing between v1 and v2

## API Integrations

### FRED API (Federal Reserve Economic Data)
- **Purpose**: Fetch economic indicators (interest rates, inflation, GDP, unemployment)
- **Implementation**: `tools.py::FredDataTools`
- **Features**:
  - Parallel fetching of multiple indicators
  - 30-second timeout per API call
  - Retry logic with exponential backoff
  - Partial result support on failures
  - Data freshness timestamps

### Exa API (Neural Search)
- **Purpose**: Find portfolio-relevant news and market analysis
- **Implementation**: `tools.py::ExaSearchTools`
- **Features**:
  - Enhanced queries with portfolio context
  - Relevance scoring (high/medium/low)
  - Trusted financial news sources
  - 30-second timeout protection
  - Graceful error handling

## Setup Instructions

### 1. Install Dependencies
```bash
cd agent
poetry install
```

### 2. Configure API Keys
Copy `.env.example` to `.env` and add your keys:
```bash
cp .env.example .env
```

Required environment variables:
- `FRED_API_KEY`: Get free at https://fred.stlouisfed.org/docs/api/api_key.html
- `EXA_API_KEY`: Contact team for access or visit https://exa.ai
- `OPENAI_API_KEY`: Required for LLM operations

### 3. Run Tests
```bash
# Run all Market Analysis v2 tests
pytest tests/test_market_analysis_v2/

# Run with coverage
pytest tests/test_market_analysis_v2/ --cov=market_analysis_v2

# Run specific test file
pytest tests/test_market_analysis_v2/test_tools.py
```

## Usage Example

```python
import asyncio
from market_analysis_v2.tools import FredDataTools, ExaSearchTools

async def analyze_market():
    # Initialize tools
    fred_tools = FredDataTools()
    exa_tools = ExaSearchTools()

    # Fetch economic data
    economic_data = await fred_tools.get_economic_indicators()

    # Search for relevant news
    portfolio = ["AAPL", "MSFT", "GOOGL"]
    news = await exa_tools.search_portfolio_news(
        query="tech sector outlook",
        portfolio_tickers=portfolio,
        num_results=5
    )

    return {
        'economic': economic_data,
        'news': news
    }

# Run the analysis
results = asyncio.run(analyze_market())
```

## Error Handling

Both tools implement comprehensive error handling:

1. **Timeout Protection**: 30-second timeout for each API call
2. **Retry Logic**: Up to 3 attempts with exponential backoff
3. **Partial Results**: Returns successful data even if some calls fail
4. **Clear Error Messages**: User-friendly error reporting
5. **Logging**: Detailed logging for debugging

## Testing

The test suite covers:
- ✅ Successful API calls
- ✅ Partial failures
- ✅ Timeout scenarios
- ✅ Complete failures
- ✅ Retry mechanisms
- ✅ Portfolio relevance scoring
- ✅ Parallel execution

## Next Steps

After API integration is complete:
1. Implement Agno v2 workflow (`workflow.py`)
2. Define specialized agents (`agents.py`)
3. Update router for v1/v2 handling
4. Create frontend components
5. Implement streaming infrastructure

## File Structure

```
market_analysis_v2/
├── __init__.py       # Package initialization
├── tools.py          # API integration tools
├── workflow.py       # Agno v2 workflow (TODO)
├── agents.py         # Agent definitions (TODO)
└── README.md         # This file
```

## Dependencies

- `fredapi`: Official FRED API Python client
- `exa-py`: Official Exa neural search client
- `agno`: Workflow orchestration framework
- `asyncio`: Asynchronous execution
- `pandas`: Data manipulation (FRED returns pandas Series)