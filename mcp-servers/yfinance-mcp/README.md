# Yahoo Finance MCP Server

MCP server for Yahoo Finance data retrieval using the yfinance library.

## Available Tools

- `get_ticker_info` - Retrieve stock data including company info, financials, trading metrics
- `get_ticker_news` - Fetch recent news articles for a stock symbol
- `search` - Search Yahoo Finance for quotes and news
- `get_top` - Get top entities (ETFs, mutual funds, companies) in a sector
- `get_price_history` - Fetch historical price data

## Running Locally

### Option 1: Using uvx (Recommended)
```bash
uvx yfmcp@latest
```

### Option 2: Using MCP Inspector
```bash
npx @modelcontextprotocol/inspector uvx yfmcp@latest
```

### Option 3: From Source
```bash
cd src
python server.py
```

## Building the Container

### Build with Podman
```bash
podman build -t yfinance-mcp:latest -f Containerfile .
```

### Build with Docker
```bash
docker build -t yfinance-mcp:latest -f Containerfile .
```

## Running the Container

**Note**: MCP servers use STDIO transport by default and wait for JSON-RPC messages on stdin. When you run the container interactively without sending messages, it will appear to hang because it's waiting for input.

### Run with Podman
```bash
# The server will wait for JSON-RPC messages on stdin (appears to hang - this is normal)
podman run -it --rm yfinance-mcp:latest
```

### Run with Docker
```bash
# The server will wait for JSON-RPC messages on stdin (appears to hang - this is normal)
docker run -it --rm yfinance-mcp:latest
```

## Testing the Container

### Basic Test: List Available Tools

Test the containerized server by sending MCP protocol messages. Note that you need to initialize the connection first:

```bash
# Test with Podman
podman run -i --rm yfinance-mcp:latest <<< '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}, "id": 1}
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}'

# Test with Docker
docker run -i --rm yfinance-mcp:latest <<< '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}, "id": 1}
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}'
```

### OpenShift Compatibility Test

Verify the container runs with arbitrary UIDs (simulates OpenShift's random UID assignment):

```bash
# Test with arbitrary UID 1000700000
podman run -i --rm --user 1000700000 yfinance-mcp:latest <<< '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}, "id": 1}
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}'

# Should return the same list of tools, confirming proper file permissions
```

### Expected Response

All tests should return a JSON response listing the 5 available tools:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_ticker_info",
        "description": "Retrieve stock data including company info, financials, trading metrics and governance data.",
        ...
      },
      {
        "name": "get_ticker_news",
        "description": "Fetches recent news articles related to a specific stock symbol...",
        ...
      },
      {
        "name": "search",
        "description": "Fetches and organizes search results from Yahoo Finance...",
        ...
      },
      {
        "name": "get_top",
        "description": "Get top entities (ETFs, mutual funds, companies, growth companies, or performing companies) in a sector.",
        ...
      },
      {
        "name": "get_price_history",
        "description": "Fetch historical price data for a given stock symbol...",
        ...
      }
    ]
  }
}
```

## File Structure

```
mcp-servers/yfinance-mcp/
├── Containerfile          # Container build definition
├── requirements.txt       # Python dependencies
├── .containerignore      # Files to exclude from container
├── README.md             # This file
└── src/
    ├── server.py         # Main MCP server
    └── yfmcp_types.py    # Type definitions
```

## Dependencies

- mcp >= 1.0.0
- fastmcp >= 0.1.0
- yfinance >= 0.2.0
- loguru >= 0.7.0
- pydantic >= 2.0.0

## Container Details

- **Base Image**: Red Hat UBI9 Python 3.11
- **User**: 1001 (non-root)
- **Working Directory**: /app
- **Exposed Port**: 8000 (for future HTTP transport support)
- **Transport**: STDIO (default)
