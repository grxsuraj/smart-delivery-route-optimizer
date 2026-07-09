"""
route_engine_loader.py - Loads the C++ Dijkstra module (pybind11) if available,
otherwise falls back to a pure-Python implementation.
Kept separate so routes.py doesn't need to know which engine is running.
"""

import sys
sys.path.insert(0, "cpp")

try:
    import route_engine
    USING_CPP = True
except ImportError:
    USING_CPP = False


def python_dijkstra(graph, source, destination):
    import heapq
    dist = {source: 0}
    prev = {}
    pq = [(0, source)]
    visited = set()

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        if u == destination:
            break
        for v, w in graph.get(u, []):
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    if destination not in dist:
        return {"path": [], "total_time": -1, "found": False}

    path = [destination]
    cur = destination
    while cur != source:
        cur = prev[cur]
        path.append(cur)
    path.reverse()
    return {"path": path, "total_time": dist[destination], "found": True}


def find_shortest_path(graph, source, destination):
    """Uses the C++ engine if built, otherwise the Python fallback above."""
    if USING_CPP:
        return route_engine.find_shortest_path(graph, source, destination)
    return python_dijkstra(graph, source, destination)
