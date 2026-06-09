*This project has been created as part of the 42 curriculum by aben-sal.*

# Fly-in

## Description

Fly-in is a Python project that simulates a fleet of drones moving through a network of connected zones.

The goal of the project is to move all drones from a start hub to an end hub while respecting the movement rules and constraints as defined in the subject.

The program:

* parses a map file,
* builds a graph of zones and connections,
* finds valid paths from the start hub to the end hub,
* distributes drones across the available paths,
* simulates the drone movements turn by turn,
* prints the movements using the required output format.

Each output line represents one simulation turn. Drones that move during that turn are printed on the same line.

Example:

```text
Turn 1: D1-A D2-B
Turn 2: D1-C D2-D
Turn 3: D1-E D2-E
```

## Instructions

### Requirements

This project uses Python 3.10 or later. No external graph libraries were used.

### Install

```bash
make install
```

### Run

```bash
make run
```

The map file used by `make run` can be changed inside the `Makefile`.

You can also run the program manually:

```bash
python3 main.py map-name.txt
```

## Algorithm and Implementation Strategy

The project uses Dijkstra's algorithm for pathfinding.

Dijkstra is used to find the cheapest path from the start hub to the end hub. Zone types affect the path cost:

* normal zones cost 1,
* priority zones cost 1,
* restricted zones cost 2,
* blocked zones are ignored and cannot be used in paths.

To find multiple paths, the program repeatedly searches for paths while banning already-used middle zones. This helps distribute drones across different routes and reduces conflicts.

The simulation moves drones turn by turn. During each turn, the program checks:

* whether the destination zone has enough capacity,
* whether the connection has enough capacity,
* whether a drone is currently flying toward a restricted zone,
* whether the drone has already arrived from a restricted move during this turn.

Drones wait when they cannot move safely.

The start and end zones are special:

* all drones can begin at the start zone,
* multiple drones can finish at the end zone.

For restricted zones, movement takes 2 turns.

Example:

```text
Turn 1: D1-A-C
Turn 2: D1-C
```

`D1-A-C` means the drone is moving on the connection from `A` toward restricted zone `C`.

`D1-C` means the drone has arrived at `C` on the next turn.

## Visual Representation

The simulation uses colored terminal output to make the movement easier to read.

Colors used:

* normal and priority zones: blue,
* restricted zones: red,
* start and end zones: green.

This helps show important zone types directly in the terminal output and makes the simulation easier to follow during testing and peer evaluation.

The colors are implemented using ANSI escape codes.

## Benchmark Results

All mandatory benchmark targets are passed.

| Map | Turns | Target |
|---|---:|---:|---|
| 01_linear_path.txt | 4 | <= 6 |
| 02_simple_fork.txt | 6 | <= 8 |
| 03_basic_capacity.txt | 4 | <= 6 |
| 01_dead_end_trap.txt | 8 | <= 12 |
| 02_circular_loop.txt | 15 | <= 15 |
| 03_priority_puzzle.txt | 8 | <= 12 |
| 01_maze_nightmare.txt | 13 | <= 30 |
| 02_capacity_hell.txt | 16 | <= 35 |
| 03_ultimate_challenge.txt | 26 | <= 45 |
| 01_the_impossible_dream.txt | 67 | 45 reference |

The Challenger map is used as a stress test. My implementation solves it in 67 turns.

## Resources

Resources used while working on this project:

* ANSI terminal colors: https://student.cs.uwaterloo.ca/~cs452/terminal.html
* MYPY command line: https://mypy.readthedocs.io/en/stable/command_line.html
* Dijkstra/pathfinding video resources:

  * https://www.youtube.com/watch?v=EFg3u_E6eHU&t=83s
  * https://www.youtube.com/watch?v=71Z-Jpnm3D4&t=2s
  * https://www.youtube.com/watch?v=CmIQ29cUGiE&t=147s
  * https://www.youtube.com/watch?v=OrJ004Wid4o&t=1363s
  * https://www.youtube.com/shorts/orSFsNhK4XE

## AI Usage

The code was created, tested, and adapted manually.
AI was used as a learning and debugging tool during this project.
