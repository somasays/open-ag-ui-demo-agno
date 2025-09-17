"""
Market Analysis v2 Package

This package implements the Market Analysis feature using Agno v2 patterns
with Step objects and explicit Agent definitions, while maintaining complete
isolation from existing v1 code.
"""

from .tools import FredDataTools, ExaSearchTools

__all__ = [
    'FredDataTools',
    'ExaSearchTools'
]

# These will be added when the workflow and agents modules are implemented:
# from .workflow import market_analysis_workflow
# from .agents import (
#     query_parser_agent,
#     economic_analyst_agent,
#     news_analyst_agent,
#     impact_synthesizer_agent
# )