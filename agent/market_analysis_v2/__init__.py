"""
Market Analysis v2 Package

This package implements the Market Analysis feature using Agno v2 patterns
with Step objects and explicit Agent definitions, while maintaining complete
isolation from existing v1 code.
"""

from .tools import FredDataTools, ExaSearchTools
from .workflow import market_analysis_workflow
from .agents import (
    query_parser_agent,
    economic_analyst_agent,
    news_analyst_agent,
    impact_synthesizer_agent,
    get_agent_for_step,
)

__all__ = [
    # Tools
    'FredDataTools',
    'ExaSearchTools',
    # Workflow
    'market_analysis_workflow',
    # Agents
    'query_parser_agent',
    'economic_analyst_agent',
    'news_analyst_agent',
    'impact_synthesizer_agent',
    'get_agent_for_step',
]