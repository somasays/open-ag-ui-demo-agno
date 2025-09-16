@// Import CopilotKit runtime components for AI agent integration
import {
  CopilotRuntime, // Core runtime for managing AI agents and conversations
  copilotRuntimeNextJSAppRouterEndpoint, // Next.js App Router integration helper
  OpenAIAdapter, // Adapter for OpenAI-compatible API endpoints
} from "@copilotkit/runtime";

// Import Next.js request type for proper TypeScript typing
import { NextRequest } from "next/server";

// Import HttpAgent for communicating with external AI agents
import { HttpAgent } from "@ag-ui/client";

// STEP 1: Initialize HTTP Agent for Stock Analysis Backend
// Create agent connection to our FastAPI stock analysis service
const agnoAgent = new HttpAgent({
  // Use environment variable for backend URL, fallback to localhost
  url: process.env.NEXT_PUBLIC_AGNO_URL || "http://0.0.0.0:8000/agno-agent",
});

// STEP 2: Configure OpenAI Service Adapter
// Set up adapter for OpenAI-compatible API communication
const serviceAdapter = new OpenAIAdapter();

// STEP 3: Initialize CopilotKit Runtime
// Create the main runtime that orchestrates AI agent interactions
const runtime = new CopilotRuntime({
  agents: {
    // Our FastAPI endpoint URL
    // @ts-ignore - Suppress TypeScript error for agent configuration
    agnoAgent: agnoAgent, // Register our stock analysis agent
  },
});

// Alternative simple runtime configuration (commented out)
// const runtime = new CopilotRuntime()

// STEP 4: Define POST Request Handler
// Export async function to handle incoming POST requests from CopilotKit
export const POST = async (req: NextRequest) => {
  // STEP 5: Create Request Handler with CopilotKit Integration
  // Configure the endpoint handler with our runtime and service adapter
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime, // Our configured CopilotKit runtime with agents
    serviceAdapter, // OpenAI adapter for LLM communication
    endpoint: "/api/copilotkit", // This API route's endpoint path
  });

  // STEP 6: Process and Return Request
  // Delegate request handling to CopilotKit's built-in handler
  // This will route requests to appropriate agents and handle responses
  return handleRequest(req);
};
