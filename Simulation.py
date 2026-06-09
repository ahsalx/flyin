Edge = tuple[str, str]
Path = list[str]
Zones = dict[str, dict[str, str | int]]
Connections = dict[Edge, dict[str, int]]
Flying = list[tuple[Edge, int] | None]


class Simulation:
    """Run the drone movement simulation."""

    BLUE = "\033[94m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    RESET = "\033[0m"

    def __init__(
        self,
        nb_drones: int,
        paths: list[Path],
        zones: Zones,
        connections: Connections,
        start: str,
        end: str,
    ) -> None:
        """Create a new simulation."""
        self.nb_drones = nb_drones
        self.paths = paths
        self.zones = zones
        self.connections = connections
        self.start = start
        self.end = end
        self.positions: list[int] = [0 for _ in range(nb_drones)]
        self.flying: Flying = [None for _ in range(nb_drones)]
        self.turn = 0

    @staticmethod
    def edge_key(zone_a: str, zone_b: str) -> Edge:
        """Return a sorted connection key."""
        if zone_a < zone_b:
            return zone_a, zone_b

        return zone_b, zone_a

    @staticmethod
    def color_movement(
        text: str,
        zone: str,
        zones: Zones,
        start: str,
        end: str,
    ) -> str:
        """Color one movement based on the destination zone."""
        if zone == start or zone == end:
            return Simulation.GREEN + text + Simulation.RESET

        if zones[zone]["zone"] == "restricted":
            return Simulation.RED + text + Simulation.RESET

        return Simulation.BLUE + text + Simulation.RESET

    @staticmethod
    def count_flying_links(flying: Flying) -> dict[Edge, int]:
        """Count links used by restricted moves."""
        used_links = {}

        for item in flying:                                                                      #item = (("a", "restricted_zone"), 2)
            if item is None:
                continue

            edge = item[0]

            if edge not in used_links:
                used_links[edge] = 0

            used_links[edge] += 1

        return used_links

    @staticmethod
    def count_occupied(
        nb_drones: int,
        paths: list[Path],
        positions: list[int],
        start: str,
        end: str,
    ) -> tuple[dict[str, int], int]:
        """Count occupied zones and finished drones."""
        occupied = {}
        finished = 0

        for i in range(nb_drones):
            path_id = i % len(paths)
            path = paths[path_id]
            position = positions[i]
            current_zone = path[position]

            if current_zone == end:
                finished += 1
                continue

            if current_zone != start and current_zone != end:
                if current_zone not in occupied:
                    occupied[current_zone] = 0

                occupied[current_zone] += 1

        return occupied, finished

    @staticmethod
    def has_zone_space(
        next_zone: str,
        occupied: dict[str, int],
        zones: Zones,
        start: str,
        end: str,
    ) -> bool:
        """Check if the next zone has space."""
        if next_zone == start or next_zone == end:
            return True

        if next_zone not in occupied:
            occupied[next_zone] = 0

        capacity = int(zones[next_zone]["max_drones"])

        return occupied[next_zone] < capacity

    @staticmethod
    def has_link_space(
        edge: Edge,
        used_links: dict[Edge, int],
        connections: Connections,
    ) -> bool:
        """Check if the connection has space."""
        if edge not in used_links:
            used_links[edge] = 0

        capacity = connections[edge]["max_link_capacity"]

        return used_links[edge] < capacity

    @staticmethod
    def finish_restricted_moves(
        nb_drones: int,
        paths: list[Path],
        positions: list[int],
        flying: Flying,
        movements: list[str],
        zones: Zones,
        start: str,
        end: str,
    ) -> set[int]:
        """Finish drones flying to restricted zones."""
        arrived_this_turn = set()

        for i in range(nb_drones):
            item = flying[i]

            if item is None:
                continue

            path_id = i % len(paths)
            path = paths[path_id]

            target_position = item[1]
            positions[i] = target_position
            flying[i] = None

            zone = path[target_position]
            text = f"D{i + 1}-{zone}"

            movements.append(
                Simulation.color_movement(text, zone, zones, start, end)
            )

            arrived_this_turn.add(i)

        return arrived_this_turn

    def print_capacity_info(self, occupied, used_links):
        print("Capacity info:")
        print("Zones:")

        for name, data in self.zones.items():
            if name == self.start or name == self.end:
                continue

            current_drones = occupied.get(name, 0)
            max_drones = data["max_drones"]

            print(f"  {name}: {current_drones}/{max_drones} drones")

        print("Connections:")
        for edge, data in self.connections.items():
            zone_a, zone_b = edge
            current_usage = used_links.get(edge, 0)
            max_capacity = data["max_link_capacity"]

            print(f"  {zone_a}-{zone_b}: {current_usage}/{max_capacity} capacity used")

    def run(self) -> None:
        """Run the simulation."""
        while True:
            movements: list[str] = []

            used_links = self.count_flying_links(self.flying)

            arrived_this_turn = self.finish_restricted_moves(
                self.nb_drones,
                self.paths,
                self.positions,
                self.flying,
                movements,
                self.zones,
                self.start,
                self.end,
            )

            occupied, finished = self.count_occupied(
                self.nb_drones,
                self.paths,
                self.positions,
                self.start,
                self.end,
            )

            if finished == self.nb_drones:
                if movements:
                    self.turn += 1
                    print(f"Turn {self.turn}: " + " ".join(movements))
                    self.print_capacity_info(occupied, used_links)
                break

            for i in range(self.nb_drones):
                if i in arrived_this_turn:
                    continue

                if self.flying[i] is not None:
                    continue

                path_id = i % len(self.paths)
                path = self.paths[path_id]
                position = self.positions[i]
                current_zone = path[position]

                if current_zone == self.end:
                    continue

                next_position = position + 1
                next_zone = path[next_position]
                edge = self.edge_key(current_zone, next_zone)

                if not self.has_link_space(
                    edge,
                    used_links,
                    self.connections,
                ):
                    continue

                if not self.has_zone_space(
                    next_zone,
                    occupied,
                    self.zones,
                    self.start,
                    self.end,
                ):
                    continue

                used_links[edge] += 1

                if current_zone != self.start and current_zone != self.end:
                    occupied[current_zone] -= 1

                if self.zones[next_zone]["zone"] == "restricted":
                    self.flying[i] = (edge, next_position)

                    if next_zone != self.start and next_zone != self.end:
                        if next_zone not in occupied:
                            occupied[next_zone] = 0

                        occupied[next_zone] += 1

                    text = f"D{i + 1}-{current_zone}-{next_zone}"
                    movements.append(
                        self.color_movement(
                            text,
                            next_zone,
                            self.zones,
                            self.start,
                            self.end,
                        )
                    )
                    continue

                self.positions[i] = next_position

                if next_zone != self.start and next_zone != self.end:
                    if next_zone not in occupied:
                        occupied[next_zone] = 0

                    occupied[next_zone] += 1

                text = f"D{i + 1}-{next_zone}"
                movements.append(
                    self.color_movement(
                        text,
                        next_zone,
                        self.zones,
                        self.start,
                        self.end,
                    )
                )

            if movements:
                self.turn += 1
                print(f"Turn {self.turn}: " + " ".join(movements))
                self.print_capacity_info(occupied, used_links)
            else:
                print("Simulation stuck")
                break
