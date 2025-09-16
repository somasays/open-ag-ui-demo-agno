# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Context7 Integration

### Automatic Documentation Lookup
**Always use Context7 MCP tools proactively** when working with:
- Code generation requiring library documentation
- Setup or configuration steps for new libraries
- API documentation and usage examples
- Framework-specific patterns and best practices

When implementing features or fixing issues that involve external libraries:
1. Automatically resolve library IDs using Context7 tools
2. Fetch relevant documentation without explicit user request
3. Use official documentation to ensure correct implementation
4. Reference documentation sources in code comments when appropriate

This proactive documentation lookup ensures accurate, up-to-date implementations based on official sources rather than assumptions.

## GitHub Workflow

### Important: Always Use GitHub CLI
**Never create commits or PRs without linking to GitHub issues.** All work should be tracked through GitHub for visibility and collaboration.

### Task Management
Always use GitHub Issues for tracking high-level tasks and features. Use the `gh` CLI for all GitHub operations:

```bash
# View existing issues
gh issue list
gh issue view <number>

# Create new issue for tasks/features
gh issue create --title "Feature: <description>" --body "Details..."

# Update issue status
gh issue comment <number> -b "Progress update..."
gh issue close <number> --comment "Completed with..."

# Link commits to issues (use in commit messages)
git commit -m "Implement feature X (#<issue-number>)"
```

### Pull Request Workflow
```bash
# Create feature branch
git checkout -b feature/<issue-number>-<brief-description>

# After implementation, push and create PR
git push -u origin HEAD
gh pr create --title "Fix #<issue-number>: <description>" \
  --body "## Summary\n- Changes made\n\n## Test Plan\n- How to test"

# Review and merge
gh pr view <number>
gh pr checks <number>
gh pr merge <number> --squash
```

### Commit Best Practices
- Reference issues in commits: `git commit -m "Add portfolio analysis (#123)"`
- Use conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Always link to relevant issue numbers

## Essential Commands

### Backend (FastAPI Agent)
```bash
cd agent
poetry install                # Install dependencies
poetry run python main.py      # Start the agent server (port 8000)
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install                  # Install dependencies
pnpm run dev                  # Start dev server with Turbopack (port 3000)
pnpm run build                # Build for production
pnpm run lint                 # Run linting
```

### Environment Setup
Both frontend and agent require `.env` files with `OPENAI_API_KEY`. Example:
```env
OPENAI_API_KEY=<<your-openai-key-here>>
```

## Architecture Overview

### System Design
This is an AI-powered stock portfolio analysis application using a decoupled architecture:
- **Frontend**: Next.js 15 with TypeScript, using CopilotKit for AI chat integration
- **Backend**: FastAPI Python agent using Agno framework for workflow orchestration
- **Communication**: HTTP streaming via ag-ui protocol for real-time agent responses

### Backend Agent Architecture

#### Core Workflow (`stock_analysis.py`)
The agent uses Agno's workflow system with three main steps:
1. **Parse Investment Request**: Extracts stock tickers, amounts, timeframes from user input
2. **Investment Analysis**: Fetches historical data via yfinance, calculates returns
3. **Generate Insights**: Creates bull/bear insights using GPT-4o-mini

#### Event Streaming (`main.py`)
- Implements Server-Sent Events (SSE) for real-time updates
- Handles both tool calls (charts/analysis) and text responses
- Uses ag-ui EventEncoder for protocol-compliant event formatting

#### Key Agent Components
- `RunAgentInput`: Receives state (cash, portfolio) and conversation history
- `StateDeltaEvent`: Incremental state updates to UI
- `TextMessageContentEvent`: Streams text responses with typing effect
- `ToolCallEvent`: Triggers UI actions like chart rendering

### Frontend Architecture

#### CopilotKit Integration (`/api/copilotkit/route.ts`)
- Bridges frontend to backend agent via HttpAgent
- Uses OpenAIAdapter for LLM communication
- Routes requests to `agnoAgent` at port 8000

#### State Management (`page.tsx`)
- `useCoAgent`: Manages agent state (cash, portfolio)
- `useCopilotAction`: Handles agent tool calls for rendering charts/analysis
- Portfolio state includes performance data, allocations, returns, insights

#### Component Structure
- `PromptPanel`: Chat interface with available cash display
- `GenerativeCanvas`: Displays portfolio visualizations
- `CashPanel`: Shows investment summary and cash management
- Chart components: `LineChartComponent`, `BarChartComponent`, `AllocationTableComponent`

### Data Flow
1. User enters investment query in chat
2. CopilotKit sends to `/api/copilotkit` route
3. Route forwards to FastAPI agent at port 8000
4. Agent processes via Agno workflow steps
5. Results stream back via SSE events
6. Frontend renders charts/insights via CopilotActions

### Key Integration Points
- **Tool Calls**: Agent returns `render_standard_charts_and_table` or `render_custom_charts` functions
- **State Updates**: Agent sends incremental updates via `StateDeltaEvent`
- **Real-time Streaming**: Uses EventEncoder for SSE protocol compliance
- **Dynamic Rendering**: Charts render based on agent-provided data structure

## Important Implementation Details

### Agent Tool Functions
The agent defines tools for UI rendering that must match frontend CopilotActions:
- `render_standard_charts_and_table`: Full portfolio visualization
- `render_custom_charts`: Sandbox/experimental visualizations
- `extract_investment_params`: Parses user investment requests
- `generate_investment_insights`: Creates AI-powered analysis

### Frontend-Agent Contract
- Agent state must include: `available_cash`, `investment_summary`, `investment_portfolio`
- Tool calls must provide: `performanceData`, `percent_allocation_per_stock`, `percent_return_per_stock`
- Insights format: `bullInsights` and `bearInsights` arrays with title, description, emoji

### Error Handling
- Backend validates stock tickers before fetching data
- Frontend shows loading states during agent processing
- Tool logs tracked via `tool_logs` array in state

## Development Process

### Starting New Features
1. **Create GitHub Issue First**:
   ```bash
   gh issue create --title "Feature: <name>" \
     --body "## Description\n\n## Acceptance Criteria\n\n## Technical Approach"
   ```

2. **Track Progress in Issue**:
   - Update issue with implementation details
   - Link related PRs and commits
   - Document any blockers or changes

3. **Complete Feature**:
   ```bash
   gh issue close <number> --comment "Implemented in PR #<pr-number>"
   ```

### Bug Fixes
```bash
# Create bug report
gh issue create --title "Bug: <description>" \
  --label "bug" \
  --body "## Steps to Reproduce\n\n## Expected Behavior\n\n## Actual Behavior"

# Fix and reference in commit
git commit -m "fix: resolve portfolio calculation error (#<issue-number>)"
```

### Documentation Updates
```bash
# Track documentation needs
gh issue create --title "Docs: <what-needs-documenting>" --label "documentation"

# Update and close
git commit -m "docs: update API documentation (#<issue-number>)"
gh issue close <number>
```

### Repository Configuration
This repository uses a fork workflow:
- **Remote**: `git@github-personal:somasays/open-ag-ui-demo-agno.git`
- **Upstream**: Original repository for syncing updates

```bash
# View repository info
gh repo view

# Check PR status
gh pr status

# Create draft PR for work in progress
gh pr create --draft --title "WIP: Feature implementation (#<issue>)"

# Mark PR ready for review
gh pr ready <number>
```

### Issue-Driven Development
1. **Before ANY code changes**, check for or create an issue:
   ```bash
   gh issue list --state open
   gh issue create --title "Task: <description>"
   ```

2. **Link ALL commits to issues**:
   ```bash
   git commit -m "feat: add market analysis (#<issue>)"
   git commit -m "fix: resolve hydration error (#<issue>)"
   git commit -m "refactor: improve agent workflow (#<issue>)"
   ```

3. **Update issues with progress**:
   ```bash
   gh issue comment <number> -b "Started implementation, created branch feature/<number>"
   gh issue comment <number> -b "Completed testing, ready for review in PR #<pr>"
   ```