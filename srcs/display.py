from srcs.models import Zone, StartZone, EndZone, BlockedZone, RestrictedZone, PriorityZone
from srcs.models import Connection
from srcs.map import Map
from srcs.parser import Parser

RESET = "\033[0m"

COLORS: dict[str, str] = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

DEFAULT_COLORS: dict[type, str] = {
    StartZone: COLORS["green"],
    EndZone: COLORS["blue"],
    BlockedZone: COLORS["red"],
    RestrictedZone: COLORS["magenta"],
    PriorityZone: COLORS["cyan"],
    Zone: COLORS["white"],
}


def _color_for(zone: Zone) -> str:
    """Return the ANSI color code to use for a zone."""
    if zone.color in COLORS:
        return COLORS[zone.color]
    return DEFAULT_COLORS.get(type(zone), COLORS["white"])


def _connector_line(r1: int, c1: int, r2: int, c2: int) -> list[tuple[int, int, str]]:
    """Interpolate a straight line between two canvas cells (Bresenham-style).

    Returns the intermediate (row, col, char) cells, excluding both endpoints.
    """
    dr = r2 - r1
    dc = c2 - c1
    steps = max(abs(dr), abs(dc))
    if steps == 0:
        return []
    if dr == 0:
        char = "-"
    elif dc == 0:
        char = "|"
    elif (dr > 0) == (dc > 0):
        char = "\\"
    else:
        char = "/"
    positions = []
    for step in range(1, steps):
        t = step / steps
        positions.append((round(r1 + dr * t), round(c1 + dc * t), char))
    return positions


def build_grid(hubs: dict[str, Zone], connections: list[Connection]) -> str:
    """Render the hubs and their connections as a colored ASCII grid."""
    if not hubs:
        return "(no hub to display)"

    zones = list(hubs.values())
    by_coord: dict[tuple[int, int], Zone] = {
        (zone.absc, zone.ordinate): zone for zone in zones
    }
    width = max(len(zone.name) for zone in zones)
    gap = 2
    min_x = min(zone.absc for zone in zones)
    max_x = max(zone.absc for zone in zones)
    min_y = min(zone.ordinate for zone in zones)
    max_y = max(zone.ordinate for zone in zones)

    def row_of(y: int) -> int:
        return max_y - y

    def col_of(x: int) -> int:
        return (x - min_x) * (width + gap)

    n_rows = max_y - min_y + 1
    n_cols = (max_x - min_x) * (width + gap) + width
    canvas = [[" "] * n_cols for _ in range(n_rows)]

    for x in range(min_x, max_x + 1):
        for y in range(min_y, max_y + 1):
            if (x, y) not in by_coord:
                canvas[row_of(y)][col_of(x) + width // 2] = "·"

    for connection in connections:
        z1, z2 = connection.zone1, connection.zone2
        r1, c1 = row_of(z1.ordinate), col_of(z1.absc) + width // 2
        r2, c2 = row_of(z2.ordinate), col_of(z2.absc) + width // 2
        for row, col, char in _connector_line(r1, c1, r2, c2):
            canvas[row][col] = char

    lines = []
    for r, row_chars in enumerate(canvas):
        row_str = "".join(row_chars)
        offset = 0
        for x in range(min_x, max_x + 1):
            zone = by_coord.get((x, max_y - r))
            if zone is None:
                continue
            color = _color_for(zone)
            start = col_of(x) + offset
            end = start + width
            label = zone.name.center(width)
            row_str = row_str[:start] + color + label + RESET + row_str[end:]
            offset += len(color) + len(RESET)
        lines.append(row_str)
    return "\n".join(lines)


def list_connections(connections: list[Connection]) -> str:
    """Render the connections as a plain text list."""
    if not connections:
        return "(no connection to display)"
    return "\n".join(
        f"{c.zone1.name} -- {c.zone2.name} (capacity={c.capacity})"
        for c in connections
    )


def display_map(map_obj: Map) -> None:
    """Print a static view of the map: hub grid then connections list."""
    print("=== Map ===")
    print(build_grid(map_obj.hubs, map_obj.connects))
    print()
    print("=== Connections ===")
    print(list_connections(map_obj.connects))


if __name__ == "__main__":
    parser = Parser()
    parser.check_file("test.txt")
    parser.connections_builder()
    display_map(parser.map_builder())
