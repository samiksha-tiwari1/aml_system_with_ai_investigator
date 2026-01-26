"""
graph_service.py

Contains logic to analyze relationships between accounts
and detect suspicious money flow patterns like loops.
"""


def build_graph(links: list[tuple[str, str]]) -> dict:
    """
    Builds adjacency list graph from account links.

    links example:
    [
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
    ]
    """
    graph = {}

    for a, b in links:
        graph.setdefault(a, []).append(b)

    return graph


def detect_cycle(graph: dict, start: str, visited=None, path=None) -> bool:
    """
    DFS to detect if there is a cycle starting from an account.
    """
    if visited is None:
        visited = set()
    if path is None:
        path = set()

    visited.add(start)
    path.add(start)

    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            if detect_cycle(graph, neighbor, visited, path):
                return True
        elif neighbor in path:
            return True

    path.remove(start)
    return False


def check_money_loop(links: list[tuple[str, str]]) -> bool:
    """
    Main function to check if any cycle exists in account graph.
    """
    graph = build_graph(links)

    for node in graph:
        if detect_cycle(graph, node):
            return True

    return False