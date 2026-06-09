import sys

from MapParser import MapParser
from PathFinder import PathFinder
from Simulation import Simulation


def main() -> None:
    if len(sys.argv) == 3:
        if sys.argv[2] or sys.argv[1] == "--capacity-info":
            if sys.argv[1] ==  "--capacity-info":
                filename = sys.argv[2]
            else:
                filename = sys.argv[1]
        print(filename)
    try:
        nb_drones, start_hub, end_hub, zones, graph, connections = MapParser.parse_file(
            filename
        )
        paths = PathFinder.find_paths(
            zones,
            graph,
            start_hub,
            end_hub,
        )

        simulation = Simulation(
            nb_drones,
            paths,
            zones,
            connections,
            start_hub,
            end_hub,
        )

        simulation.run()
        print(f"Turns: {simulation.turn}")





    except FileNotFoundError:
        print(f"Error: file not found: {filename}")
    except ValueError as error:
        print(f"Error: {error}")



    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        return

    filename = sys.argv[1]
    print(filename)
    try:
        nb_drones, start_hub, end_hub, zones, graph, connections = MapParser.parse_file(
            filename
        )

        paths = PathFinder.find_paths(
            zones,
            graph,
            start_hub,
            end_hub,
        )

        simulation = Simulation(
            nb_drones,
            paths,
            zones,
            connections,
            start_hub,
            end_hub,
        )

        simulation.run()
        print(f"Turns: {simulation.turn}")

    except FileNotFoundError:
        print(f"Error: file not found: {filename}")
    except ValueError as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()






# import os
# maps = os.listdir("maps")

# for name in maps:
#     print(f"{name}")
#     os.system(f"python3 main.py maps/{name}")