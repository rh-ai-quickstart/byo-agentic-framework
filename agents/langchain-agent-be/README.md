# LangChain 1.0 MCP Agent Backend

FastAPI backend using LangChain 1.0's `create_agent` with MCP (Model Context Protocol) tools.

## Overview

This backend is based on the work in [2-langchain-v1-mcp-agent.ipynb](../../assets/notebooks/2-langchain-v1-mcp-agent.ipynb) and provides a REST API for interacting with an AI agent that has access to weather tools via MCP.

## Setup

### 1. Install Dependencies

```bash
# From project root
cd agents/langchain-agent-be

# Install using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure your `.env` file exists in the project root with:

```bash
LLAMA_STACK_OPENAI_ENDPOINT=https://llama-stack-lls-demo.apps.XXX/v1/openai/v1
INFERENCE_MODEL=maas/Llama-4-Scout-17B-16E-W4A16
API_KEY=fake
MCP_WEATHER_SERVER_URL=http://mcp-weather-lls-demo.apps.XXX/sse
```

### 3. Run the Server

```bash
# Quick start with startup script (recommended)
./start.sh

# Or using Python directly
python app.py

# Or with uvicorn from venv
../../.venv/bin/uvicorn app:app --reload --port 8080

# Or activate venv first, then run uvicorn
cd ../..
source .venv/bin/activate
cd agents/langchain-agent-be
uvicorn app:app --reload --port 8080
```

The server will start on `http://localhost:8080`

**Note:** The `start.sh` script automatically checks dependencies and environment variables before starting.

## API Endpoints

### Health Check

```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_ready": true,
  "tools_loaded": 1
}
```

### Configuration

```bash
GET /config
```

**Response:**
```json
{
  "model": "maas/Llama-4-Scout-17B-16E-W4A16",
  "endpoint": "https://llama-stack-lls-demo.../v1/openai/v1",
  "mcp_server": "http://mcp-weather-lls-demo.../sse",
  "tools_count": 1
}
```

### List Tools

```bash
GET /tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "getforecast",
      "description": "Get real time weather forecast for a location"
    }
  ]
}
```

### Ask Question (Detailed)

```bash
POST /ask
Content-Type: application/json

{
  "query": "What's the weather in Boston?"
}
```

**Response:**
```json
{
  "query": "What's the weather in Boston?",
  "messages": [
    {
      "role": "user",
      "content": "What's the weather in Boston?",
      "tool_calls": null
    },
    {
      "role": "assistant",
      "content": "",
      "tool_calls": [
        {
          "name": "getforecast",
          "args": {"latitude": "42.358429", "longitude": "-71.059573"}
        }
      ]
    },
    {
      "role": "tool",
      "content": "Forecast for 42.358429, -71.059573: ...",
      "tool_calls": null
    },
    {
      "role": "assistant",
      "content": "The weather in Boston is...",
      "tool_calls": null
    }
  ],
  "final_response": "The weather in Boston is..."
}
```

### Ask Question (Simple)

```bash
POST /ask/simple
Content-Type: application/json

{
  "query": "What's the weather in Boston?"
}
```

**Response:**
```json
{
  "response": "The weather in Boston is partly cloudy with a temperature of 55°F..."
}
```

### Using the Interactive Docs

FastAPI provides automatic interactive API documentation:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Architecture

```
┌─────────────────────────────────────────────┐
│         FastAPI Backend                     │
│         (app.py)                            │
└────────┬────────────────────┬───────────────┘
         │                    │
         │ Model Calls        │ Tool Execution
         ▼                    ▼
┌─────────────────┐   ┌──────────────────────┐
│  Llama Stack    │   │  MCP Client          │
│  (OpenAI API)   │   │  (langchain-mcp)     │
│  - vLLM         │   │  - SSE Transport     │
│  - Llama Model  │   │  - Tool Adapters     │
└─────────────────┘   └──────┬───────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ MCP Server   │
                      │ (Weather)    │
                      └──────────────┘
```


## References

- [Notebook: 2-langchain-v1-mcp-agent.ipynb](../../assets/notebooks/2-langchain-v1-mcp-agent.ipynb)
- [LangChain 1.0 create_agent](https://docs.langchain.com/oss/python/langchain/agents)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MCP Documentation](https://docs.langchain.com/oss/python/langchain/mcp)
