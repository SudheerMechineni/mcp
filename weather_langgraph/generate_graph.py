import networkx as nx
import matplotlib.pyplot as plt

# Define nodes and edges as in the LangGraph workflow
nodes = [
    "query_parser", "time", "geocode", "preference", "cache", "weather", "alert", "playground", "activities", "response_formatter", "retry_weather", "retry_alert", "activity_loop", "fallback", "notification", "audit", "playground_booking"
]
edges = [
    ("query_parser", "time"),
    ("time", "geocode"),
    ("query_parser", "preference"),
    ("preference", "activities"),
    ("geocode", "cache"),
    ("cache", "weather"),
    ("weather", "notification"),
    ("weather", "playground_booking"),
    ("playground_booking", "response_formatter"),
    ("geocode", "audit"),
    ("weather", "audit"),
    ("alert", "audit"),
    ("activities", "audit"),
    ("playground", "audit"),
    ("response_formatter", "audit"),
    ("fallback", "response_formatter"),
    ("geocode", "weather"),
    ("geocode", "alert"),
    ("weather", "playground"),
    ("weather", "activities"),
    ("alert", "activities"),
    ("alert", "playground"),
    ("activities", "response_formatter"),
    ("playground", "response_formatter"),
    ("geocode", "retry_weather"),
    ("geocode", "retry_alert"),
    ("retry_weather", "activity_loop"),
    ("retry_alert", "activity_loop"),
    ("activity_loop", "response_formatter")
]

G = nx.DiGraph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

plt.figure(figsize=(16, 10))
pos = nx.spring_layout(G, seed=42)
nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=10, arrowsize=20)
plt.title("LangGraph Multi-Agent Workflow")
plt.savefig("langgraph_workflow.png")
plt.close()
print("Graph saved as langgraph_workflow.png")
