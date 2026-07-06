import sys
import pygame as py

from models import (
    Zone, StartZone, EndZone, BlockedZone, RestrictedZone, PriorityZone,
)
from map import Map
from parser import Parser

BACKGROUND = (18, 18, 22)
GRID_DOT = (55, 55, 62)
LINE_COLOR = (140, 140, 150)
LABEL_COLOR = (235, 235, 235)
BORDER_COLOR = (15, 15, 15)
START_BORDER = (60, 220, 120)
END_BORDER = (230, 70, 70)

COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "black": (20, 20, 20),
    "red": (220, 60, 60),
    "green": (60, 190, 100),
    "yellow": (230, 200, 50),
    "blue": (60, 120, 230),
    "magenta": (200, 70, 200),
    "cyan": (70, 200, 200),
    "white": (235, 235, 235),
}

DEFAULT_COLOR_BY_TYPE: dict[type, tuple[int, int, int]] = {
    StartZone: COLOR_MAP["green"],
    EndZone: COLOR_MAP["blue"],
    BlockedZone: COLOR_MAP["red"],
    RestrictedZone: COLOR_MAP["magenta"],
    PriorityZone: COLOR_MAP["cyan"],
    Zone: COLOR_MAP["white"],
}

CELL = 110
MARGIN = 90
LEGEND_WIDTH = 230
NODE_RADIUS = 26


def _color_for(zone: Zone) -> tuple[int, int, int]:
    """Explicit color option wins, otherwise fall back to a default by type."""
    if zone.color in COLOR_MAP:
        return COLOR_MAP[zone.color]
    return DEFAULT_COLOR_BY_TYPE.get(type(zone), COLOR_MAP["white"])


class GraphicDisplay():
    """Static pygame view of a Map: colored hub nodes, connections, legend."""

    def __init__(self, map_obj: Map) -> None:
        self.map = map_obj
        self.hubs = list(map_obj.hubs.values())
        self._compute_layout()
        py.init()
        py.display.set_caption("fly_in - map view")
        self.font = py.font.SysFont(None, 20)
        self.title_font = py.font.SysFont(None, 24, bold=True)
        size = (self.width + LEGEND_WIDTH, self.height)
        self.screen = py.display.set_mode(size)
        self.clock = py.time.Clock()

    def _compute_layout(self) -> None:
        xs = [h.absc for h in self.hubs]
        ys = [h.ordinate for h in self.hubs]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)
        self.width = (self.max_x - self.min_x) * CELL + 2 * MARGIN
        self.height = (self.max_y - self.min_y) * CELL + 2 * MARGIN

    def _pixel(self, zone: Zone) -> tuple[int, int]:
        x = MARGIN + (zone.absc - self.min_x) * CELL
        y = MARGIN + (self.max_y - zone.ordinate) * CELL
        return x, y

    def _draw_grid(self) -> None:
        for x in range(self.min_x, self.max_x + 1):
            for y in range(self.min_y, self.max_y + 1):
                px = MARGIN + (x - self.min_x) * CELL
                py_coord = MARGIN + (self.max_y - y) * CELL
                py.draw.circle(self.screen, GRID_DOT, (px, py_coord), 2)

    def _draw_connections(self) -> None:
        for c in self.map.connects:
            x1, y1 = self._pixel(c.zone1)
            x2, y2 = self._pixel(c.zone2)
            width = 1 + c.capacity
            py.draw.line(self.screen, LINE_COLOR, (x1, y1), (x2, y2), width)
            if c.capacity > 1:
                mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                label = self.font.render(str(c.capacity), True, LABEL_COLOR)
                self.screen.blit(label, label.get_rect(center=(mx, my)))

    def _draw_hubs(self) -> None:
        for zone in self.hubs:
            x, y = self._pixel(zone)
            border = BORDER_COLOR
            if isinstance(zone, StartZone):
                border = START_BORDER
            elif isinstance(zone, EndZone):
                border = END_BORDER
            py.draw.circle(self.screen, _color_for(zone), (x, y), NODE_RADIUS)
            py.draw.circle(self.screen, border, (x, y), NODE_RADIUS, 3)
            label = self.font.render(zone.name, True, LABEL_COLOR)
            label_pos = (x, y + NODE_RADIUS + 12)
            self.screen.blit(label, label.get_rect(center=label_pos))

    def _draw_legend(self) -> None:
        x0 = self.width + 20
        y = 20
        title = self.title_font.render("Legend", True, LABEL_COLOR)
        self.screen.blit(title, (x0, y))
        y += 34
        restricted_color = DEFAULT_COLOR_BY_TYPE[RestrictedZone]
        entries = [
            ("Start", DEFAULT_COLOR_BY_TYPE[StartZone], START_BORDER),
            ("End", DEFAULT_COLOR_BY_TYPE[EndZone], END_BORDER),
            ("Normal", DEFAULT_COLOR_BY_TYPE[Zone], BORDER_COLOR),
            ("Blocked", DEFAULT_COLOR_BY_TYPE[BlockedZone], BORDER_COLOR),
            ("Restricted", restricted_color, BORDER_COLOR),
            ("Priority", DEFAULT_COLOR_BY_TYPE[PriorityZone], BORDER_COLOR),
        ]
        for name, fill, border in entries:
            py.draw.circle(self.screen, fill, (x0 + 12, y + 10), 10)
            py.draw.circle(self.screen, border, (x0 + 12, y + 10), 10, 2)
            label = self.font.render(name, True, LABEL_COLOR)
            self.screen.blit(label, (x0 + 32, y + 2))
            y += 28

    def _draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self._draw_grid()
        self._draw_connections()
        self._draw_hubs()
        self._draw_legend()
        py.display.flip()

    def run(self) -> None:
        is_active = True
        while is_active:
            for event in py.event.get():
                if event.type == py.QUIT:
                    is_active = False
                elif event.type == py.KEYDOWN and event.key == py.K_ESCAPE:
                    is_active = False
            self._draw()
            self.clock.tick(30)
        py.quit()


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "test.txt"
    parser = Parser()
    parser.check_file(path)
    parser.connections_builder()
    GraphicDisplay(parser.map_builder()).run()
