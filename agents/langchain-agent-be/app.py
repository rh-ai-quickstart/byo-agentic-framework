"""
FastAPI LangChain 1.0 Agent with MCP Tools

Based on: assets/notebooks/2-langchain-v1-mcp-agent.ipynb
Uses LangChain 1.0 create_agent with MCP (Model Context Protocol) adapters
"""

import os
import logging
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import uvicorn

# LangChain 1.0 imports
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# MCP Adapters for client-side tool execution
from langchain_mcp_adapters.client import MultiServerMCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration from environment
LLAMA_STACK_OPENAI_ENDPOINT = os.getenv("LLAMA_STACK_OPENAI_ENDPOINT")
INFERENCE_MODEL = os.getenv("INFERENCE_MODEL")
API_KEY = os.getenv("API_KEY", "fake")
MCP_WEATHER_SERVER_URL = os.getenv("MCP_WEATHER_SERVER_URL")

logger.info(f"Llama Stack Endpoint: {LLAMA_STACK_OPENAI_ENDPOINT}")
logger.info(f"Inference Model: {INFERENCE_MODEL}")
logger.info(f"MCP Weather Server: {MCP_WEATHER_SERVER_URL}")

# Initialize FastAPI app
app = FastAPI(
    title="LangChain 1.0 MCP Agent API",
    version="1.0.0",
    description="FastAPI backend using LangChain 1.0 create_agent with MCP tools"
)

# Global variables for agent and MCP client
agent = None
mcp_client = None
tools = []

@app.on_event("startup")
async def startup_event():
    """Initialize LLM, MCP client, and agent on startup"""
    global agent, mcp_client, tools

    logger.info("Starting up FastAPI LangChain 1.0 Agent...")

    # Initialize LLM
    llm = ChatOpenAI(
        model=INFERENCE_MODEL,
        api_key=API_KEY,
        base_url=LLAMA_STACK_OPENAI_ENDPOINT,
        temperature=0.0,
    )
    logger.info(f"LLM initialized: {INFERENCE_MODEL}")

    # Initialize MCP client and get tools
    logger.info("Setting up MCP client...")
    mcp_client = MultiServerMCPClient({
        "weather": {
            "transport": "sse",
            "url": MCP_WEATHER_SERVER_URL,
        }
    })

    tools = await mcp_client.get_tools()
    logger.info(f"Loaded {len(tools)} tools from MCP server:")
    for tool in tools:
        logger.info(f"   - {tool.name}: {tool.description}")

    # Create LangChain 1.0 agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
You are a helpful weather assistant.

You have access to weather tools that can retrieve current weather information.
When a user asks about weather, use the available tools to get accurate data.

Always:
- Be concise and friendly
- Use tools when needed to get real data
- Provide clear, actionable information
""".strip(),
    )
    logger.info("Agent created successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global mcp_client
    logger.info("Shutting down...")
    # MCP client cleanup would go here if needed

# Request/Response models
class QueryRequest(BaseModel):
    query: str

class Message(BaseModel):
    role: str
    content: str
    tool_calls: List[Dict[str, Any]] | None = None

class QueryResponse(BaseModel):
    query: str
    messages: List[Message]
    final_response: str

# Health check
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_ready": agent is not None,
        "tools_loaded": len(tools)
    }

# Configuration endpoint
@app.get("/config")
def get_config():
    """Get backend configuration"""
    return {
        "model": INFERENCE_MODEL,
        "endpoint": LLAMA_STACK_OPENAI_ENDPOINT,
        "mcp_server": MCP_WEATHER_SERVER_URL,
        "tools_count": len(tools)
    }

# Tools endpoint
@app.get("/tools")
def get_tools_list():
    """List available MCP tools"""
    return {
        "tools": [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in tools
        ]
    }

# Main query endpoint
@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    """
    Process user query using LangChain 1.0 agent with MCP tools

    Returns conversation trace and final response
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    logger.info(f"User query: {request.query}")

    try:
        # Invoke agent
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": request.query}]
        })

        # Parse messages
        messages = []
        final_response = ""

        for message in result["messages"]:
            if isinstance(message, HumanMessage):
                messages.append(Message(
                    role="user",
                    content=message.content
                ))

            elif isinstance(message, AIMessage):
                tool_calls = None
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls = [
                        {
                            "name": tc['name'],
                            "args": tc['args']
                        }
                        for tc in message.tool_calls
                    ]
                    logger.info(f"Tool calls: {tool_calls}")

                messages.append(Message(
                    role="assistant",
                    content=message.content,
                    tool_calls=tool_calls
                ))

                # Last AI message without tool calls is final response
                if not tool_calls:
                    final_response = message.content

            elif isinstance(message, ToolMessage):
                messages.append(Message(
                    role="tool",
                    content=message.content
                ))
                logger.info(f"Tool result: {message.content[:100]}...")

        logger.info(f"Query completed successfully")

        return QueryResponse(
            query=request.query,
            messages=messages,
            final_response=final_response
        )

    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Simple endpoint for just getting the final answer
@app.post("/ask/simple")
async def ask_simple(request: QueryRequest):
    """
    Simple endpoint that returns only the final response
    """
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    logger.info(f"Simple query: {request.query}")

    try:
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": request.query}]
        })

        # Get last AI message
        final_response = ""
        for message in reversed(result["messages"]):
            if isinstance(message, AIMessage) and message.content:
                if not (hasattr(message, 'tool_calls') and message.tool_calls):
                    final_response = message.content
                    break

        return {"response": final_response}

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Launch server
if __name__ == "__main__":
    port = int(os.getenv('PORT', '8080'))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
