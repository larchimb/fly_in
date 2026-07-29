*This project has been created as part of the 42 curriculum by larchimb.*

# Fly In

## Description

Fly In simulates a fleet of drones navigating from a start hub to an end hub
through a network of interconnected zones. The program parses a text map
describing hubs (normal, blocked, restricted, priority) and the connections
between them, computes optimal paths for each drone, runs the simulation
turn by turn, and renders the result as an animated 2D visualization.

## Instructions

### Requirements
- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (dependency manager)

### Installation
```
make install
```

### Execution
```
make run ARG="path/to/map.txt"
```

### Debug mode
```
make debug ARG="path/to/map.txt"
```

### Linting
```
make lint          # flake8 + mypy (project-required flags)
make lint-strict    # flake8 + mypy --strict
```

### Clean
```
make clean
```

## Algorithm & Implementation Strategy

The map is parsed into `Zone` objects (and subclasses `StartZone`, `EndZone`,
`BlockedZone`, `RestrictedZone`, `PriorityZone`) linked by `Connection`
objects. An adjacency list (`hubs_connected`) is built for every non-blocked
zone.

Path costs are precomputed once with a Dijkstra's algorithm run backward
from the end hub (`path_for_hub`), giving every zone its minimal distance
to the destination. `RestrictedZone` hubs have a higher traversal cost,
naturally discouraging their use unless they shorten the path.

Each simulation turn, every drone picks its next hop greedily
(`pick_target`): among its directly connected neighbors, it selects the
closest-to-end zone that still has free capacity, prioritizing
`PriorityZone` hubs first. Connection capacity is enforced so drones cannot
overload a link, and zones/connections free up as drones move past them.

## Visual Representation

The simulation is rendered with `pygame`. Each zone type has a distinct
default color (green for start, blue for end, red for blocked, yellow for
restricted, magenta for priority), and a legend is drawn at the bottom of
the screen mapping colors to zone types. Drones are shown as moving circles
interpolated smoothly between hubs, and the terminal prints each drone's
move at every turn for a textual trace alongside the animation. The
simulation can be paused (`space`) or exited (`escape`) at any time.

## Example

Input file `simple_map.txt`:
```
nb_drones: 1
start_hub: start 0 0
hub: relay 1 0
end_hub: goal 2 0
connection: start-relay
connection: relay-goal
```

Run:
```
make run ARG="simple_map.txt"
```

Terminal output (one line per turn, `drone_id-target_hub`):
```
D1-relay
D1-goal
```

Alongside this trace, a pygame window opens showing the three hubs aligned
and connected by black lines — `start` in green, `relay` in the default
color, `goal` in blue — with drone `D1` animated moving smoothly from
`start` to `relay`, then from `relay` to `goal`.

## Resources

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [pygame documentation](https://www.pygame.org/docs/)
- [pygame documentation](https://zestedesavoir.com/tutoriels/846/pygame-pour-les-zesteurs/1381_a-la-decouverte-de-pygame/creer-une-simple-fenetre-personnalisable/)

**AI usage**: Claude was used throughout development for
algorithmic complexity analysis, dead-code detection, code review of the
Dijkstra/pathfinding logic, explaining mypy/flake8 errors, and drafting
this README.
