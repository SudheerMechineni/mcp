# Weather API MCP Server

This project provides a Model Context Protocol (MCP) server for fetching weather alerts and forecasts using the National Weather Service (NWS) API, and demonstrates a multi-agent LangGraph workflow for intelligent activity and playground booking suggestions.

## Features

- Get active weather alerts for any US state
- Get weather forecast for any location (latitude, longitude)
- Multi-agent workflow using LangGraph
- Book playground automatically if weather is good (Sunny/Clear)
- Suggest activities based on weather, user preferences, and date
- Caching, retry, fallback, notification, and audit agents for robustness
- Health check MCP tool

## Requirements

- Python 3.10+
- [mcp](https://pypi.org/project/mcp/) package
- [httpx](https://pypi.org/project/httpx/)
- [langgraph](https://pypi.org/project/langgraph/)

## Installation

1. Clone the repository or download the project files.
2. Install dependencies:

```zsh
pip install mcp httpx langgraph
```

## Usage

To run the MCP server:

```zsh
python langgraph_multi_agent.py
```

This will start the MCP server using stdio transport. You can interact with the server using MCP-compatible clients or tools.

## Example Multi-Agent Workflow

- User asks: "Can I book the playground in Sacramento tomorrow? What activities do you suggest?"
- Agents parse query, extract location, date, and preferences
- Weather and alert agents fetch real data
- Playground is booked automatically if weather is good
- Activities are suggested based on weather and user preferences
- All decisions and data are logged for audit

## API Tools

- `get_alerts(state: str) -> str`: Returns active weather alerts for a given US state code (e.g., CA, NY).
- `get_forecast(latitude: float, longitude: float) -> str`: Returns a weather forecast for the specified latitude and longitude.
- `suggest_activities(state: str, latitude: float, longitude: float) -> str`: Suggests activities and playground booking based on real weather.
- `health_check() -> str`: Health check for MCP server.

## Prompts

Here are prompt suggestions to validate all major scenarios for your multi-agent workflow:

###### Weather Queries

* "What's the weather in Sacramento today?"
* "Will it rain in San Francisco tomorrow?"
* "Is it sunny in Los Angeles?"

###### Playground Booking

* "Can I book the playground in Sacramento if the weather is good?"
* "Book the playground in San Francisco for tomorrow."
* "Is playground booking recommended in Seattle today?"

###### Activity Suggestions

* "Suggest outdoor activities for Sacramento."
* "What indoor activities can I do in San Francisco if it rains?"
* "Recommend activities for cloudy weather in New York."

###### Branching/Conditional Logic

* "Should I book the playground in Sacramento if it's raining?"
* "What should I do if the weather is not clear in Los Angeles?"

###### Weather Alerts

* "Are there any weather alerts for California?"
* "Show active weather alerts for New York."

###### Cache Logic

* "What's the weather in Sacramento today?" (Run twice to test cache hit/miss.)
* "Get the weather for San Francisco today." (Then repeat to check cache.)

###### Audit Logging

* "Show me the audit log for my weather query in Sacramento."
* "What decisions were made for my playground booking in San Francisco?"

###### User Preferences

* "I prefer indoor activities in Sacramento."
* "Suggest outdoor activities for tomorrow in Los Angeles."

###### Fallback/Notification

* "Book the playground in Sacramento if the weather changes."
* "Notify me if the weather changes after booking the playground."

###### MCP Tools/Health Check

* "Run a health check on the weather multi-agent MCP server."
* "Use MCP tools to get the forecast for Sacramento."

These prompts will help you validate weather, booking, activities, branching, cache, audit, preferences, alerts, fallback, notification, and MCP tool integration.

## Agents in Workflow

- QueryParserAgent
- TimeAgent
- GeocodeAgent
- WeatherAgent
- AlertAgent
- ActivityAgent
- PlaygroundAgent
- PlaygroundBookingAgent (books playground if weather is good)
- PreferenceAgent
- CacheAgent
- RetryAgent
- ActivityLoopAgent
- NotificationAgent
- AuditAgent
- FallbackAgent
- ResponseFormatterAgent

## About

This project demonstrates how to build a robust, extensible MCP server in Python using LangGraph, with real-world multi-agent orchestration for weather, activities, and playground booking.
