"""
Multi-agent LangGraph example for weather and location tasks.
"""
import os
import openai
import langgraph as lg
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP
import httpx
import re
import logging
import networkx as nx

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Best Practice: Use logging instead of print for better observability
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather_multi_agent")

# Define agent behaviors
# LangGraph does not provide an Agent base class. Use simple Python classes for agents.
class WeatherAgent:
    """Agent to fetch weather information for a location."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        location = state.get("location")
        if not location:
            return {"weather": "No location provided."}
        # Dummy response, replace with real API call
        return {"weather": f"Sunny in {location}"}

class LocationAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query")
        if not query:
            return {"location": "No query provided."}
        # Dummy response, replace with real location lookup
        return {"location": "Sacramento, CA"}

class PlaygroundAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        weather = state.get("weather", "")
        if "Sunny" in weather:
            return {"playground": "You can book the playground!"}
        return {"playground": "Playground booking not recommended due to weather."}

class ActivityAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        weather = state.get("weather", "")
        if "Sunny" in weather:
            return {"activities": "Outdoor activities: soccer, tennis, picnic."}
        elif "Rain" in weather:
            return {"activities": "Indoor activities: board games, reading, movies."}
        else:
            return {"activities": "Check local events or try creative indoor hobbies."}

    def __repr__(self):
        return "<ActivityAgent>"

class QueryParserAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "")
        if not query or not isinstance(query, str):
            logger.warning("Query is missing or not a string.")
            return {"location_name": "Sacramento, CA", "intent": "weather", "query": ""}
        # Simple location extraction (improve with NLP if needed)
        match = re.search(r'in ([A-Za-z ,]+)', query)
        location = match.group(1).strip() if match else "Sacramento, CA"
        intent = "weather"
        if "activity" in query or "suggest" in query:
            intent = "activity"
        elif "book" in query or "playground" in query:
            intent = "booking"
        return {"location_name": location, "intent": intent, "query": query}

DEFAULT_LOCATION = "Sacramento, CA"
DEFAULT_LATITUDE = 38.5816
DEFAULT_LONGITUDE = -121.4944

class GeocodeAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        location_name = state.get("location_name", DEFAULT_LOCATION)
        # Dummy geocoding for demo
        # In real use, call geocoding API
        if location_name.lower() == DEFAULT_LOCATION.lower():
            return {"latitude": DEFAULT_LATITUDE, "longitude": DEFAULT_LONGITUDE, **state}
        return {"latitude": 37.7749, "longitude": -122.4194, **state}  # SF fallback

class AlertAgent:
    """Agent to fetch weather alerts for a location."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Use MCP tool for alerts
        import asyncio
        state = state.copy()
        # Use the correct MCP tool name
        state["alerts"] = asyncio.run(get_lg_alerts("CA"))
        return state

class ResponseFormatterAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        response = f"Location: {state.get('location_name')}\nWeather: {state.get('weather')}\nActivities: {state.get('activities')}\nPlayground: {state.get('playground')}\nAlerts: {state.get('alerts')}"
        return {"response": response}

class RetryAgent:
    def __init__(self, agent, max_retries=2):
        self.agent = agent
        self.max_retries = max_retries
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        for attempt in range(self.max_retries):
            result = self.agent.run(state)
            # Assume any value not containing 'Unable' or 'No' is success
            if not any(v for v in result.values() if isinstance(v, str) and ("Unable" in v or "No" in v)):
                return result
        # Return last result after retries
        return result

class ActivityLoopAgent:
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Suggest multiple activities for each weather period
        activities = []
        forecast = state.get("forecast", "")
        # Use the correct MCP tool name for forecast
        if not forecast and "latitude" in state and "longitude" in state:
            import asyncio
            forecast = asyncio.run(get_lg_forecast(state["latitude"], state["longitude"]))
        for line in forecast.split("\n---\n"):
            if "Sunny" in line or "Clear" in line:
                activities.append(f"{line}: Outdoor activities: soccer, tennis, picnic.")
            elif "Rain" in line or "Showers" in line:
                activities.append(f"{line}: Indoor activities: board games, reading, movies.")
            else:
                activities.append(f"{line}: Check local events or try creative indoor hobbies.")
        return {"activities": "\n".join(activities)}

class TimeAgent:
    """Extracts and normalizes date/time from the query."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "")
        # Simple demo: extract 'tomorrow', 'today', etc.
        if "tomorrow" in query:
            state["date"] = "2025-08-06"
        elif "today" in query:
            state["date"] = "2025-08-05"
        else:
            state["date"] = "2025-08-05"  # Default to today
        return state

class PreferenceAgent:
    """Handles user preferences for activities."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("query", "")
        if "indoor" in query:
            state["preference"] = "indoor"
        elif "outdoor" in query:
            state["preference"] = "outdoor"
        else:
            state["preference"] = "any"
        return state

class CacheAgent:
    """Caches recent weather/alert responses."""
    cache = {}
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        key = f"{state.get('latitude')},{state.get('longitude')},{state.get('date')}"
        if key in self.cache:
            state["cached_weather"] = self.cache[key]
            logger.info(f"Cache hit for {key}")
        else:
            state["cached_weather"] = None
            logger.info(f"Cache miss for {key}")
        return state
    def update_cache(self, key, value):
        self.cache[key] = value

class FallbackAgent:
    """Provides a default response if all other agents fail."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"response": "Sorry, we could not process your request. Please try again later."}

class NotificationAgent:
    """Sends notifications if weather changes after booking."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Demo: always notify for rain
        if "Rain" in state.get("weather", ""):
            state["notification"] = "Weather changed to rain. Playground booking cancelled."
        else:
            state["notification"] = "No weather change notification."
        return state

class AuditAgent:
    """Logs all decisions and data for traceability."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"AUDIT: {state}")
        return state

class PlaygroundBookingAgent:
    """Books playground if weather is good."""
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        weather = state.get("weather", "")
        if "Sunny" in weather or "Clear" in weather:
            state["playground_booking"] = "Playground booked!"
        else:
            state["playground_booking"] = "Playground not booked due to weather."
        return state

# Create agents
weather_agent = WeatherAgent()
location_agent = LocationAgent()
playground_agent = PlaygroundAgent()
activity_agent = ActivityAgent()
query_parser_agent = QueryParserAgent()
geocode_agent = GeocodeAgent()
alert_agent = AlertAgent()
response_formatter_agent = ResponseFormatterAgent()
time_agent = TimeAgent()
preference_agent = PreferenceAgent()
cache_agent = CacheAgent()
fallback_agent = FallbackAgent()
notification_agent = NotificationAgent()
audit_agent = AuditAgent()
playground_booking_agent = PlaygroundBookingAgent()

# Wrap WeatherAgent and AlertAgent with retry logic
retry_weather_agent = RetryAgent(weather_agent, max_retries=3)
retry_alert_agent = RetryAgent(alert_agent, max_retries=3)
activity_loop_agent = ActivityLoopAgent()

# Define graph
graph = nx.DiGraph()
graph.add_node("query_parser")
graph.add_node("geocode")
graph.add_node("weather")
graph.add_node("alert")
graph.add_node("playground")
graph.add_node("activities")
graph.add_node("response_formatter")
graph.add_node("retry_weather")
graph.add_node("retry_alert")
graph.add_node("activity_loop")
graph.add_node("time")
graph.add_node("preference")
graph.add_node("cache")
graph.add_node("fallback")
graph.add_node("notification")
graph.add_node("audit")
graph.add_node("playground_booking")

# Create a mapping from node name to agent instance
agent_map = {
    "query_parser": query_parser_agent,
    "geocode": geocode_agent,
    "weather": weather_agent,
    "alert": alert_agent,
    "playground": playground_agent,
    "activities": activity_agent,
    "response_formatter": response_formatter_agent,
    "retry_weather": retry_weather_agent,
    "retry_alert": retry_alert_agent,
    "activity_loop": activity_loop_agent,
    "time": time_agent,
    "preference": preference_agent,
    "cache": cache_agent,
    "fallback": fallback_agent,
    "notification": notification_agent,
    "audit": audit_agent,
    "playground_booking": playground_booking_agent,
}

# Edges for new agents
# QueryParserAgent → TimeAgent → GeocodeAgent
# QueryParserAgent → PreferenceAgent → ActivityAgent
# GeocodeAgent → CacheAgent → WeatherAgent
# WeatherAgent → NotificationAgent
# All agents → AuditAgent
# FallbackAgent → ResponseFormatterAgent

graph.add_edge("query_parser", "time")
graph.add_edge("time", "geocode")
graph.add_edge("query_parser", "preference")
graph.add_edge("preference", "activities")
graph.add_edge("geocode", "cache")
graph.add_edge("cache", "weather")
graph.add_edge("weather", "notification")
graph.add_edge("weather", "playground_booking")
graph.add_edge("playground_booking", "response_formatter")

# Audit edges (log after each major step)
graph.add_edge("geocode", "audit")
graph.add_edge("weather", "audit")
graph.add_edge("alert", "audit")
graph.add_edge("activities", "audit")
graph.add_edge("playground", "audit")
graph.add_edge("response_formatter", "audit")

# Fallback edge
# If response_formatter fails, fallback
# (Demo: not implemented as error handling, but node is available)
graph.add_edge("fallback", "response_formatter")

mcp = FastMCP("weather_multi_agent")
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# Best Practice: Centralized error handling for async requests
async def make_nws_request(url: str) -> dict:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/geo+json"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status error: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

@mcp.tool()
async def get_lg_alerts(state: str) -> str:
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)
    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."
    alerts = []
    for feature in data["features"]:
        props = feature["properties"]
        alerts.append(f"Event: {props.get('event', 'Unknown')}, Severity: {props.get('severity', 'Unknown')}, Desc: {props.get('description', 'No description')}")
    return "\n---\n".join(alerts)

@mcp.tool()
async def get_lg_forecast(latitude: float, longitude: float) -> str:
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)
    if not points_data:
        return "Unable to fetch forecast data for this location."
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)
    if not forecast_data:
        return "Unable to fetch detailed forecast."
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:
        forecasts.append(f"{period['name']}: {period['detailedForecast']}")
    return "\n---\n".join(forecasts)

@mcp.tool()
async def suggest_activities(state: str = None, latitude: float = None, longitude: float = None) -> str:
    """Suggest activities and playground booking based on real weather."""
    # Use forecast tool to get weather
    if latitude is not None and longitude is not None:
        forecast = await get_lg_forecast(latitude, longitude)
    elif state:
        # Use alerts as fallback
        forecast = await get_lg_alerts(state)
    else:
        return "Please provide a location (state or lat/lon)."
    # Simple logic for demo
    if "Sunny" in forecast or "Clear" in forecast:
        return "Book the playground! Suggested activities: soccer, tennis, picnic."
    elif "Rain" in forecast or "Showers" in forecast:
        return "Do not book playground. Suggested activities: board games, reading, movies."
    else:
        return f"Weather info: {forecast}\nSuggested activities: Check local events or try creative indoor hobbies."

# Best Practice: Add a health check MCP tool
@mcp.tool()
async def health_check() -> str:
    """Check if the MCP server is running and responsive."""
    return "Weather multi-agent MCP server is healthy."

def run_multi_agent(query: str):
    state = {"query": query}
    audit_log = []
    # 1. Parse query
    state = agent_map["query_parser"].run(state)
    audit_log.append(("query_parser", dict(state)))
    # 2. Extract time
    state = agent_map["time"].run(state)
    audit_log.append(("time", dict(state)))
    # 3. Geocode location
    state = agent_map["geocode"].run(state)
    audit_log.append(("geocode", dict(state)))
    # 4. Check cache (optional)
    state = agent_map["cache"].run(state)
    audit_log.append(("cache", dict(state)))
    # Branch: If cache hit, skip weather API and use cached value
    if state.get("cached_weather"):
        state["weather"] = state["cached_weather"]
        audit_log.append(("weather (cache hit)", dict(state)))
    else:
        # 5. Get weather
        state = agent_map["weather"].run(state)
        # Update cache
        key = f"{state.get('latitude')},{state.get('longitude')},{state.get('date')}"
        agent_map["cache"].update_cache(key, state["weather"])
        audit_log.append(("weather (API)", dict(state)))
    # Branch: If weather is good, book playground and suggest outdoor activities
    weather = state.get("weather", "")
    if "Sunny" in weather or "Clear" in weather:
        state = agent_map["playground_booking"].run(state)
        state["activities"] = "Outdoor activities: soccer, tennis, picnic."
        audit_log.append(("playground_booking (good)", dict(state)))
    # Branch: If weather is bad, do not book playground and suggest indoor activities
    elif "Rain" in weather or "Showers" in weather:
        state = agent_map["playground_booking"].run(state)
        state["activities"] = "Indoor activities: board games, reading, movies."
        audit_log.append(("playground_booking (bad)", dict(state)))
    # Branch: Otherwise, fallback to generic activities
    else:
        state = agent_map["playground_booking"].run(state)
        state["activities"] = "Check local events or try creative indoor hobbies."
        audit_log.append(("playground_booking (other)", dict(state)))
    # 8. Format response
    state = agent_map["response_formatter"].run(state)
    audit_log.append(("response_formatter", dict(state)))
    # Add audit log to state for inspection
    state["audit_log"] = audit_log
    return state.get("response", state)

# Best Practice: Use __name__ == "__main__" for entry point
if __name__ == "__main__":
    query = "What's the weather in Sacramento?"
    result = run_multi_agent(query)
    logger.info(result)
    import asyncio
    mcp.run(transport='stdio')
