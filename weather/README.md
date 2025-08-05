# Weather API MCP Server

This project provides a Model Context Protocol (MCP) server for fetching weather alerts and forecasts using the National Weather Service (NWS) API.

## Features

- Get active weather alerts for any US state
- Get weather forecast for any location (latitude, longitude)

## Requirements

- Python 3.10+
- [mcp](https://pypi.org/project/mcp/) package
- [httpx](https://pypi.org/project/httpx/)

## Installation

1. Clone the repository or download the project files.
2. Install dependencies:

```zsh
pip install mcp httpx
```

## Usage

To run the MCP server:

```zsh
python weather.py
```

This will start the MCP server using stdio transport. You can interact with the server using MCP-compatible clients or tools.

## Claude

Update below details in /Users/sankarvinnakota/Library/Application Support/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "weather": {
      "command": "/Users/sankarvinnakota/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/sankarvinnakota/San_No_Cloud_Sync/Learning/FSDS_AI/Class_Notes/weather",
        "run",
        "weather.py"
      ]
    }
  }
}

## Testing in Claude

What’s the weather in Sacramento?

What are the active weather alerts in Texas?

## API Tools

- `get_alerts(state: str) -> str`: Returns active weather alerts for a given US state code (e.g., CA, NY).
- `get_forecast(latitude: float, longitude: float) -> str`: Returns a weather forecast for the specified latitude and longitude.

## Project Structure

- `weather.py`: Main MCP server and API logic
- `main.py`: (Optional) Entry point for other scripts
- `README.md`: Project documentation
- `pyproject.toml`, `uv.lock`: Dependency and environment management

## About

This project demonstrates how to build a simple MCP server in Python to interact with external APIs and expose useful tools for weather data retrieval.
