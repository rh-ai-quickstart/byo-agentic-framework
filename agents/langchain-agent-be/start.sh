#!/bin/bash

# Startup script for LangChain 1.0 MCP Agent Backend
# Usage: ./start.sh

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting LangChain 1.0 MCP Agent Backend...${NC}\n"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: app.py not found${NC}"
    echo "Please run this script from the agents/langchain-agent-be directory"
    exit 1
fi

# Check if .env exists
if [ ! -f "../../.env" ]; then
    echo -e "${YELLOW}Warning: .env file not found in project root${NC}"
    echo "Creating from .env.example..."
    if [ -f "../../.env.example" ]; then
        cp ../../.env.example ../../.env
        echo -e "${YELLOW}Please edit ../../.env with your configuration${NC}"
        exit 1
    else
        echo -e "${RED}Error: .env.example not found${NC}"
        exit 1
    fi
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo -e "${RED}Error: Python not found${NC}"
    exit 1
fi

# Check if dependencies are installed
echo -e "${YELLOW}Checking dependencies...${NC}"
if ! ../../.venv/bin/python -c "import fastapi" &> /dev/null; then
    echo -e "${YELLOW}Dependencies not installed. Installing...${NC}"
    if command -v uv &> /dev/null; then
        cd ../..
        uv pip install -r agents/langchain-agent-be/requirements.txt
        cd agents/langchain-agent-be
    else
        ../../.venv/bin/pip install -r requirements.txt
    fi
fi

# Load environment variables and display
echo -e "${GREEN}Environment Configuration:${NC}"
source ../../.env
echo "  Endpoint: ${LLAMA_STACK_OPENAI_ENDPOINT}"
echo "  Model: ${INFERENCE_MODEL}"
echo "  MCP Server: ${MCP_WEATHER_SERVER_URL}"
echo ""

# Start the server
PORT=${PORT:-8080}
echo -e "${GREEN}Starting server on port ${PORT}...${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop${NC}\n"

# Use Python to run the app
python app.py
