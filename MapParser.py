from typing import Dict, List, Tuple

Zone = Dict[str, int | str]
Graph = Dict[str, List[str]]
Connections = Dict[Tuple[str, str], Dict[str, int]]
Zones = Dict[str, Zone]


class MapParser:
    @staticmethod
    def parse_file(filename: str) -> tuple[int, str, str, Zones, Graph, Connections]:
        """Parse drone network map file."""
        nb_drones: int | None = None
        start_hub: str | None = None
        end_hub: str | None = None
        zones: Zones = {}
        graph: Graph = {}
        connections: Connections = {}
        zones_metadata = ["color", "zone", "max_drones"]
        line_num = 0
        first_line_checked = False

        with open(filename, "r") as file:
            for line in file:
                line_num += 1
                line = line.strip()

                if "#" in line:
                    line = line.split("#", 1)[0].strip()

                if not line:
                    continue

                if not first_line_checked:
                    if not line.startswith("nb_drones:"):
                        raise ValueError(f"Line {line_num}: First line must be nb_drones")
                    first_line_checked = True

                if line.startswith("nb_drones:"):
                    if nb_drones is not None:
                        raise ValueError(f"Duplicate nb_drones [Line : {line_num}]")

                    try:
                        nb_drones = int(line.split(":", 1)[1].strip())
                    except ValueError:
                        raise ValueError(f"Invalid nb_drones [Line : {line_num}]")

                    if nb_drones <= 0:
                        raise ValueError(f"nb_drones must be positive [Line : {line_num}]")

                elif line.startswith(("start_hub:", "end_hub:", "hub:")):
                    prefix, data = line.split(":", 1)
                    data = data.strip()

                    if prefix == "start_hub":
                        if start_hub is not None:
                            raise ValueError(f"Multiple start_hub defined [Line : {line_num}]")
                        zone_type_name = "start_hub"
                    elif prefix == "end_hub":
                        if end_hub is not None:
                            raise ValueError(f"Multiple end_hub defined [Line : {line_num}]")
                        zone_type_name = "end_hub"
                    else:
                        zone_type_name = "hub"

                    meta_dict: Zone = {
                        "zone": "normal",
                        "color": "none",
                        "max_drones": 1,
                    }

                    if ("[" in data) != ("]" in data):
                        raise ValueError(f"Invalid metadata block [Line : {line_num}]")

                    if "[" in data and "]" in data:
                        main, meta = data.split("[", 1)
                        meta = meta.rstrip("]").strip()
                    else:
                        main = data
                        meta = ""

                    parts = main.split()
                    if len(parts) != 3:
                        raise ValueError(f"Invalid {zone_type_name} format [Line : {line_num}]")

                    name, x_str, y_str = parts

                    if "-" in name or " " in name: #zone names cannot contain dashes or spaces.
                        raise ValueError(f"Line {line_num}: Zone name '{name}' contains dash or space")

                    try:
                        x = int(x_str)
                        y = int(y_str)
                    except ValueError:
                        raise ValueError(f"Invalid coordinates for zone '{name}' [Line : {line_num}]")

                    if name in zones:
                        raise ValueError(f"Duplicated zone '{name}' [Line : {line_num}]")

                    if meta:
                        for attr in meta.split(): #meta.split() creates a temporary list:
                            if "=" not in attr:
                                raise ValueError(f"Invalid metadata format [Line : {line_num}]")

                            key, value = attr.split("=", 1)

                            if key not in zones_metadata:
                                raise ValueError(f"Invalid metadata key [Line : {line_num}]")

                            if key == "zone":
                                if value not in ["normal", "restricted", "priority", "blocked"]:
                                    raise ValueError(f"Invalid zone type [Line : {line_num}]")
                                meta_dict["zone"] = value

                            elif key == "max_drones":
                                try:
                                    value_int = int(value)
                                    if value_int <= 0:
                                        raise ValueError
                                except ValueError:
                                    raise ValueError(f"Invalid max_drones [Line : {line_num}]")
                                meta_dict["max_drones"] = value_int

                            elif key == "color":
                                meta_dict["color"] = value

                    zones[name] = {
                        "type": zone_type_name,
                        "x": x,
                        "y": y,
                        "zone": meta_dict["zone"],
                        "color": meta_dict["color"],
                        "max_drones": meta_dict["max_drones"],
                    }

                    graph[name] = []

                    if zone_type_name == "start_hub":
                        start_hub = name
                    elif zone_type_name == "end_hub":
                        end_hub = name

                elif line.startswith("connection:"):
                    _, data = line.split(":", 1)
                    data = data.strip()

                    if ("[" in data) != ("]" in data):
                        raise ValueError(f"Invalid metadata block [Line : {line_num}]")

                    if "[" in data and "]" in data:
                        main, meta = data.split("[", 1)
                        meta = meta.rstrip("]").strip()
                    else:
                        main = data
                        meta = ""

                    parts = main.split("-")
                    if len(parts) != 2:
                        raise ValueError(f"Invalid connection format [Line : {line_num}]")

                    z1, z2 = parts
                    z1 = z1.strip()
                    z2 = z2.strip()

                    if z1 not in zones:
                        raise ValueError(f"Invalid zone assigned {z1} [Line : {line_num}]")
                    if z2 not in zones:
                        raise ValueError(f"Invalid zone assigned {z2} [Line : {line_num}]")

                    if z1 == z2:
                        raise ValueError(f"{z1}-{z2} invalid self connection [Line : {line_num}]")

                    if z1 < z2:
                        edge_key = (z1, z2)
                    else:
                        edge_key = (z2, z1)

                    if edge_key in connections:
                        raise ValueError(f"{z1}-{z2} duplicated connection [Line : {line_num}]")

                    graph[z1].append(z2)
                    graph[z2].append(z1)

                    conn_meta: Dict[str, int] = {"max_link_capacity": 1}

                    if meta:
                        if "=" not in meta:
                            raise ValueError(f"{z1}-{z2} invalid metadata format [Line : {line_num}]")

                        attr, value = meta.split("=", 1)

                        if attr != "max_link_capacity":
                            raise ValueError(f"{z1}-{z2} invalid connection metadata format [Line : {line_num}]")

                        try:
                            value_int = int(value)
                        except ValueError:
                            raise ValueError(f"{z1}-{z2} max_link_capacity must be an integer [Line : {line_num}]")

                        if value_int <= 0:
                            raise ValueError(f"{z1}-{z2} max_link_capacity must be positive [Line : {line_num}]")

                        conn_meta["max_link_capacity"] = value_int

                    connections[edge_key] = conn_meta

                else:
                    raise ValueError(f"Invalid line format [Line : {line_num}]")

        if nb_drones is None:
            raise ValueError("Missing nb_drones")
        if start_hub is None:
            raise ValueError("Missing start_hub")
        if end_hub is None:
            raise ValueError("Missing end_hub")

        zones[start_hub]["max_drones"] = nb_drones
        zones[end_hub]["max_drones"] = nb_drones

        return nb_drones, start_hub, end_hub, zones, graph, connections