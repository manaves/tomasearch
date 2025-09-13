import os
import pickle
import networkx as nx
import requests
from io import BytesIO

# Load environment variables
GRAPH_URL = os.getenv('GRAPH_FILE_URL')

# Global variables to hold the graph and its components
G = None
COMPONENTS = []
SUBGRAPHS = []

try:
    print(f"Downloading graph from: {GRAPH_URL}")
    response = requests.get(GRAPH_URL)
    response.raise_for_status()  # Exception for HTTP errors

    f = BytesIO(response.content)
    G = pickle.load(f)
    print("Graph loaded successfully. Type:", type(G))

    # Identify connected components
    if G.is_directed():
        COMPONENTS = list(nx.weakly_connected_components(G))
    else:
        COMPONENTS = list(nx.connected_components(G))

    SUBGRAPHS = [G.subgraph(c).copy() for c in COMPONENTS]
    print(f"Subgraphs loaded: {len(SUBGRAPHS)}")

except Exception as e:
    print(f"[ERROR] Failed to load graph: {e}")

def get_graph():
    """Return the loaded graph."""
    return G
