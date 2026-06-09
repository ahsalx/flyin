from heapq import heappop, heappush #Python’s priority queue tools, list is slower
from typing import Dict, List, Set

Zone = Dict[str, int | str]
Graph = Dict[str, List[str]]
Zones = Dict[str, Zone]


class PathFinder:
    @staticmethod
    def dijkstra(
        zones: Zones,
        graph: Graph,
        start: str,
        end: str,
        banned_zones: Set[str] | None = None,
    ) -> List[str]:
        """Find the cheapest path from start to end.""" #subject asks for docstrings
        if banned_zones is None:
            banned_zones = set()

        distances: Dict[str, int] = {}
        previous: Dict[str, str | None] = {}

        for zone in zones:
            distances[zone] = 999999
            previous[zone] = None

        queue: List[tuple[int, str]] = [] #priority queue

        distances[start] = 0
        heappush(queue, (0, start))

        while queue:
            current_distance, current_zone = heappop(queue)

            if current_distance > distances[current_zone]:
                continue

            if current_zone == end:
                break

            for neighbor in graph[current_zone]:
                if neighbor in banned_zones:
                    continue

                if zones[neighbor]["zone"] == "blocked":
                    continue

                cost = 1

                if zones[neighbor]["zone"] == "restricted":
                    cost = 2

                new_distance = current_distance + cost

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_zone
                    heappush(queue, (new_distance, neighbor))

        if distances[end] == 999999:
            raise ValueError("No path found from start to end")

        path: List[str] = []
        current: str | None = end

        while current is not None:
            path.append(current)
            current = previous[current]

        path.reverse()
        return path

    @staticmethod
    def find_paths(
        zones: Zones,
        graph: Graph,
        start: str,
        end: str,
        max_paths: int = 3,
    ) -> List[List[str]]:
        """Find multiple paths from start to end. (paths that avoid sharing middle zones)"""
        paths: List[List[str]] = []
        banned_zones: Set[str] = set()

        for _ in range(max_paths):
            try:
                path = PathFinder.dijkstra(
                    zones,
                    graph,
                    start,
                    end,
                    banned_zones,
                )
            except ValueError:
                break
                
            if path in paths:
                break
            
            paths.append(path)

            for zone in path[1:-1]:
                banned_zones.add(zone)

        if not paths:
            raise ValueError("No path found from start to end")

        return paths