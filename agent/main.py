# Import necessary libraries for FastAPI web server and async operations
from fastapi import FastAPI  # Main FastAPI framework for web API
from fastapi.responses import StreamingResponse  # For streaming real-time responses to client
import uuid  # For generating unique identifiers
from typing import Any  # Type hints for better code documentation
import os  # Operating system interface for environment variables
import uvicorn  # ASGI server for running FastAPI applications
import asyncio  # Asynchronous I/O operations and event loop management

# Import event system components from ag_ui.core for real-time UI updates
from ag_ui.core import (
    RunAgentInput,  # Input data structure for agent requests
    StateSnapshotEvent,  # Event for sending current state to UI
    EventType,  # Enumeration of all possible event types
    RunStartedEvent,  # Event signaling agent run has started
    RunFinishedEvent,  # Event signaling agent run has completed
    TextMessageStartEvent,  # Event for beginning text message streaming
    TextMessageEndEvent,  # Event for ending text message streaming
    TextMessageContentEvent,  # Event for streaming text content chunks
    ToolCallStartEvent,  # Event for beginning tool/function calls
    ToolCallEndEvent,  # Event for ending tool/function calls
    ToolCallArgsEvent,  # Event for streaming tool arguments
    StateDeltaEvent,  # Event for incremental state updates
)

# Import event encoder for formatting events for streaming
from ag_ui.encoder import EventEncoder  # Encodes events for client consumption
from typing import List  # Type hint for list types

# Import the main stock analysis workflow from our custom module
from stock_analysis import stock_analysis_workflow

# Import v2 market analysis workflow (optional feature flag)
try:
    from market_analysis_v2 import market_analysis_workflow
    V2_WORKFLOW_AVAILABLE = True
except ImportError:
    V2_WORKFLOW_AVAILABLE = False

# Initialize FastAPI application instance
app = FastAPI()




# MARKET ANALYSIS V2 ENDPOINT: Handle market analysis queries with Agno v2
# This endpoint uses the new v2 workflow with Steps and Agents
@app.post("/market-analysis-v2")
async def market_analysis_v2(input_data: RunAgentInput):
    """
    Handle market analysis requests using v2 workflow.
    This uses Agno v2 patterns with Steps and Agents.
    """
    if not V2_WORKFLOW_AVAILABLE:
        return {"error": "Market Analysis v2 not available"}

    try:
        # Extract query and portfolio from input
        query = ""
        portfolio = []

        # Get the latest user message as query
        for msg in input_data.messages:
            if msg.role == "user":
                query = msg.content

        # Get portfolio from state if available
        if "investment_portfolio" in input_data.state:
            portfolio = list(input_data.state["investment_portfolio"].keys())

        # Run the market analysis workflow
        result = await market_analysis_workflow.arun(
            additional_data={
                "query": query,
                "portfolio": portfolio,
                "messages": input_data.messages,
                "available_cash": input_data.state.get("available_cash", 0),
            }
        )

        # Return structured response
        return {
            "status": "success",
            "workflow": "market_analysis_v2",
            "result": result.dict() if hasattr(result, 'dict') else str(result),
        }

    except Exception as e:
        return {"error": str(e), "workflow": "market_analysis_v2"}


# MAIN API ENDPOINT: Handle stock analysis agent requests
# This endpoint receives investment queries and streams back real-time responses
@app.post("/agno-agent")
async def agno_agent(input_data: RunAgentInput):
    try:

        # ASYNC GENERATOR: Streams events to client in real-time
        # This function generates a stream of events that get sent to the frontend
        async def event_generator():
            # Step 1: Initialize event streaming infrastructure
            encoder = EventEncoder()  # Encodes events for transmission
            event_queue = asyncio.Queue()  # Queue for handling events from workflow

            # Step 2: Define event emission callback function
            # This function gets called by workflow steps to send updates to UI
            def emit_event(event):
                event_queue.put_nowait(event)  # Add event to queue without blocking

            # Step 3: Generate unique message identifier for this conversation
            message_id = str(uuid.uuid4())

            # Step 4: Send initial "run started" event to client
            # Signals to the UI that the agent has begun processing
            yield encoder.encode(
                RunStartedEvent(
                    type=EventType.RUN_STARTED,
                    thread_id=input_data.thread_id,  # Conversation thread identifier
                    run_id=input_data.run_id,  # Unique run identifier
                )
            )

            # Step 5: Send current state snapshot to client
            # Provides initial state including cash, portfolio, and logs
            yield encoder.encode(
                StateSnapshotEvent(
                    type=EventType.STATE_SNAPSHOT,
                    snapshot={
                        "available_cash": input_data.state["available_cash"],  # User's cash balance
                        "investment_summary": input_data.state["investment_summary"],  # Portfolio summary
                        "investment_portfolio": input_data.state[
                            "investment_portfolio"  # Current holdings
                        ],
                        "tool_logs": [],  # Initialize empty tool execution logs
                    },
                )
            )
            
            # Step 6: Determine which workflow to use (v1 or v2)
            # Check if user requested market analysis (v2) vs stock analysis (v1)
            use_v2_workflow = False
            if V2_WORKFLOW_AVAILABLE and input_data.messages:
                # Check latest user message for market analysis keywords
                latest_message = input_data.messages[-1].content if input_data.messages[-1].role == "user" else ""
                market_keywords = ["market analysis", "fed", "inflation", "economic", "news analysis"]
                use_v2_workflow = any(keyword in latest_message.lower() for keyword in market_keywords)

            # Step 6a: Start the appropriate workflow as an async task
            if use_v2_workflow:
                # Use v2 market analysis workflow
                agent_task = asyncio.create_task(
                    market_analysis_workflow.arun(
                        additional_data={
                            "query": input_data.messages[-1].content if input_data.messages else "",
                            "portfolio": list(input_data.state.get("investment_portfolio", {}).keys()),
                            "messages": input_data.messages,
                            "available_cash": input_data.state["available_cash"],
                            "emit_event": emit_event,
                        }
                    )
                )
            else:
                # Use v1 stock analysis workflow (default)
                agent_task = asyncio.create_task(
                        stock_analysis_workflow.arun(  # Execute workflow asynchronously
                        additional_data= {
                            "tools": input_data.tools,  # Available tools/functions
                            "messages": input_data.messages,  # Conversation history
                            "emit_event": emit_event,  # Callback for sending UI updates
                            "available_cash": input_data.state["available_cash"],  # Cash balance
                            "investment_portfolio": input_data.state["investment_portfolio"],  # Holdings
                            "tool_logs": [],  # Initialize logs array
                        }
                    )
                )

            # Step 7: Stream events from workflow while it's running
            # This loop processes events from the workflow and streams them to client
            while True:
                try:
                    # Step 8: Wait for events from workflow (with timeout)
                    event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                    yield encoder.encode(event)  # Send event to client
                except asyncio.TimeoutError:
                    # Step 9: Check if workflow has completed
                    # Check if the agent is done
                    if agent_task.done():
                        break  # Exit loop when workflow finishes

            # Step 10: Clear tool logs after workflow completion
            # Send event to reset tool logs in UI
            yield encoder.encode(
                StateDeltaEvent(
                    type=EventType.STATE_DELTA,
                    delta=[{"op": "replace", "path": "/tool_logs", "value": []}],
                )
            )
            
            # Step 11: Process final workflow results and stream appropriate response
            # Check if the last message from assistant contains tool calls or text
            if agent_task.result().step_responses[-1].content['messages'][-1].role == "assistant":
                if agent_task.result().step_responses[-1].content['messages'][-1].tool_calls:
                    # BRANCH A: Handle tool call responses (charts, analysis, etc.)
                    # for tool_call in state['messages'][-1].tool_calls:
                    
                    # Step 12: Send tool call start event
                    yield encoder.encode(
                        ToolCallStartEvent(
                            type=EventType.TOOL_CALL_START,
                            tool_call_id=agent_task.result().step_responses[-1].content['messages'][-1].tool_calls[0].id,
                            toolCallName=agent_task.result().step_responses[-1].content['messages'][-1]
                            .tool_calls[0]
                            .function.name,  # Name of function being called (e.g., render_charts)
                        )
                    )

                    # Step 13: Send tool call arguments
                    # Stream the arguments being passed to the tool/function
                    yield encoder.encode(
                        ToolCallArgsEvent(
                            type=EventType.TOOL_CALL_ARGS,
                            tool_call_id=agent_task.result().step_responses[-1].content['messages'][-1].tool_calls[0].id,
                            delta=agent_task.result().step_responses[-1].content['messages'][-1]
                            .tool_calls[0]
                            .function.arguments,  # JSON arguments for the function call
                        )
                    )

                    # Step 14: Send tool call completion event
                    # Signals that the tool call has finished
                    yield encoder.encode(
                        ToolCallEndEvent(
                            type=EventType.TOOL_CALL_END,
                            tool_call_id=agent_task.result().step_responses[-1].content['messages'][-1].tool_calls[0].id,
                        )
                    )
                else:
                    # BRANCH B: Handle text message responses
                    # Step 15: Start text message streaming
                    # Signal to UI that a text message is beginning
                    yield encoder.encode(
                        TextMessageStartEvent(
                            type=EventType.TEXT_MESSAGE_START,
                            message_id=message_id,
                            role="assistant",  # Message from AI assistant
                        )
                    )

                    # Step 16: Stream message content (if available)
                    # Only send content event if content is not empty
                    if agent_task.result().step_responses[-1].content['messages'][-1].content:
                        content = agent_task.result().step_responses[-1].content['messages'][-1].content
                        
                        # Step 17: Split message into chunks for streaming effect
                        # Split content into 100 parts
                        n_parts = 100
                        part_length = max(1, len(content) // n_parts)  # Ensure at least 1 char per part
                        parts = [
                            content[i : i + part_length]
                            for i in range(0, len(content), part_length)
                        ]
                        
                        # Step 18: Handle edge case where splitting creates too many parts
                        # If splitting results in more than 5 due to rounding, merge last parts
                        if len(parts) > n_parts:
                            parts = parts[: n_parts - 1] + [
                                "".join(parts[n_parts - 1 :])
                            ]
                        
                        # Step 19: Stream each content chunk with delay for typing effect
                        for part in parts:
                            yield encoder.encode(
                                TextMessageContentEvent(
                                    type=EventType.TEXT_MESSAGE_CONTENT,
                                    message_id=message_id,
                                    delta=part,  # Chunk of message content
                                )
                            )
                            await asyncio.sleep(0.05)  # Small delay for typing effect
                    else:
                        # Step 20: Handle case where no content was generated
                        # Send error message if content is empty
                        yield encoder.encode(
                            TextMessageContentEvent(
                                type=EventType.TEXT_MESSAGE_CONTENT,
                                message_id=message_id,
                                delta="Something went wrong! Please try again.",
                            )
                        )

                    # Step 21: End text message streaming
                    # Signal to UI that text message is complete
                    yield encoder.encode(
                        TextMessageEndEvent(
                            type=EventType.TEXT_MESSAGE_END,
                            message_id=message_id,
                        )
                    )

            # Step 22: Send final "run finished" event
            # Signal to client that the entire agent run has completed
            yield encoder.encode(
                RunFinishedEvent(
                    type=EventType.RUN_FINISHED,
                    thread_id=input_data.thread_id,
                    run_id=input_data.run_id,
                )
            )

    except Exception as e:
        # Step 23: Handle any errors during execution
        print(e)  # Log error for debugging

    # Step 24: Return streaming response to client
    # FastAPI will stream the events as Server-Sent Events (SSE)
    return StreamingResponse(event_generator(), media_type="text/event-stream")


# SERVER STARTUP FUNCTION: Initialize and run the FastAPI server
def main():
    """Run the uvicorn server."""
    # Step 1: Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    # Step 2: Start uvicorn ASGI server with configuration
    uvicorn.run(
        "main:app",  # Module:app reference
        host="0.0.0.0",  # Listen on all network interfaces
        port=port,  # Port number
        reload=True,  # Auto-reload on code changes (development mode)
    )


# SCRIPT ENTRY POINT: Run server when script is executed directly
if __name__ == "__main__":
    main()  # Start the server
