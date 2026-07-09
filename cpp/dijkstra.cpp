// dijkstra.cpp
// Shortest-path (by time) engine for the delivery route optimizer.
// Exposed to Python via pybind11 as module `route_engine`.

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <vector>
#include <queue>
#include <limits>
#include <unordered_map>
#include <string>

namespace py = pybind11;

struct Edge {
    int to;
    double weight; // time in minutes
};

// Runs Dijkstra's algorithm on a graph given as an adjacency list.
// graph: node_id -> list of (neighbor_id, weight)
// Returns: {"path": [node_ids...], "total_time": double}
py::dict find_shortest_path(
    std::unordered_map<int, std::vector<std::pair<int, double>>> graph,
    int source,
    int destination
) {
    std::unordered_map<int, double> dist;
    std::unordered_map<int, int> prev;

    // Priority queue of (distance, node) — min-heap
    using PQItem = std::pair<double, int>;
    std::priority_queue<PQItem, std::vector<PQItem>, std::greater<PQItem>> pq;

    dist[source] = 0.0;
    pq.push({0.0, source});

    while (!pq.empty()) {
        auto [d, u] = pq.top();
        pq.pop();

        if (dist.count(u) && d > dist[u]) continue; // stale entry
        if (u == destination) break;

        if (graph.count(u)) {
            for (auto& [v, w] : graph[u]) {
                double newDist = d + w;
                if (!dist.count(v) || newDist < dist[v]) {
                    dist[v] = newDist;
                    prev[v] = u;
                    pq.push({newDist, v});
                }
            }
        }
    }

    py::dict result;

    if (!dist.count(destination)) {
        // No path found
        result["path"] = std::vector<int>{};
        result["total_time"] = -1.0;
        result["found"] = false;
        return result;
    }

    // Reconstruct path by walking backwards
    std::vector<int> path;
    int current = destination;
    path.push_back(current);
    while (current != source) {
        current = prev[current];
        path.push_back(current);
    }
    std::reverse(path.begin(), path.end());

    result["path"] = path;
    result["total_time"] = dist[destination];
    result["found"] = true;
    return result;
}

PYBIND11_MODULE(route_engine, m) {
    m.doc() = "C++ Dijkstra shortest-path engine for delivery route optimizer";
    m.def("find_shortest_path", &find_shortest_path,
          "Find shortest time-path between source and destination node IDs",
          py::arg("graph"), py::arg("source"), py::arg("destination"));
}
