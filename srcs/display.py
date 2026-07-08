from srcs.models import MapError, Zone, StartZone, EndZone, BlockedZone, Connection, Drone, DroneState, Colors, DisplayError
import pygame as py
from enum import Enum


class Map():
    def __init__(self,
                 start: StartZone | Zone,
                 end: EndZone | Zone,
                 hubs: dict[str, Zone],
                 connections: list[Connection],
                 nb_drones: int) -> None:
        self.start = start
        self.end = end
        self.hubs = hubs
        self.connects = connections
        self.drones: list[Drone] = []
        self.create_drones_list(nb_drones)
        self.path_finder()
        self.turn_moved = 0
        self.total_moved = 0

    def create_drones_list(self, nb_drones: int) -> None:
        """Create the drones list"""
        for i in range(1, nb_drones + 1):
            self.drones.append(Drone("D{i}", self.start))

    def path_finder(self) -> None:
        """Compute, via Dijkstra from 'end', the minimal cost for each zone to reach the end"""
        hub_passed: set[Zone] = set()
        self.end.path_to_end = 0
        remaining = set(self.hubs.values())
        if isinstance(self.end, BlockedZone):
            raise MapError("The end is a blocked hub")
        while remaining:
            zone = min(remaining, key=lambda z: z.path_to_end)
            remaining.remove(zone)
            if zone.path_to_end == float("inf"):
                break
            hub_passed.add(zone)

            for neighbor in zone.hubs_connected:
                if neighbor in hub_passed:
                    continue
                if isinstance(neighbor, BlockedZone):
                    remaining.remove(neighbor)
                    continue

                new_cost = zone.path_to_end + neighbor.cost
                if new_cost < neighbor.path_to_end:
                    neighbor.path_to_end = new_cost


class MapDisplay():
    """Static pygame view of a Map: colored hub nodes, connections, legend."""
    def __init__(self, map: Map) -> None:
        self.map = map
        py.init()
        self.initialize_settings()
        self.initialize_screen()

    def initialize_settings(self) -> None:
        """Initializing settings for the display"""
        self.margin = 100
        self.legend = 200
        self.hub_radius = 30
        self.drone_radius = 10
        self.gap = 150
        self.clock = py.time.Clock()
        self.font = py.font.SysFont(None, 20)

        abscissas = [z.absc for z in self.map.hubs.values()]
        ordinates = [z.ordinate for z in self.map.hubs.values()]
        self.min_x = min(abscissas)
        self.max_x = max(abscissas)
        self.min_y = min(ordinates)
        self.max_y = max(ordinates)

        self.width = (self.max_x - self.min_x) * self.gap + 2 * self.margin
        self.height = (
            (self.max_y - self.min_y) * self.gap + 2 * self.margin + self.legend
            )
        self.size = (self.width, self.height)
        if self.width > 3500:
            print(self.width)
            raise DisplayError("Width is too large for this map")
        if self.height > 2000:
            raise DisplayError("Height is too high for this map")

    def initialize_screen(self) -> None:
        """Initialize the empty screen"""
        self.screen = py.display.set_mode(self.size)
        py.display.set_caption("Fly_in")
        is_active = True

        for hub in self.map.hubs.values():
            x = (hub.absc - self.min_x) * self.gap + self.margin
            y = (hub.ordinate - self.min_y) * self.gap + self.margin
            place = (x, y)
            py.draw.circle(self.screen, hub.color.value, place, self.hub_radius)
            label = self.font.render(hub.name, True, Colors.WHITE.value)
            label_pos = (x, y + self.hub_radius + 12)
            self.screen.blit(label, label.get_rect(center=label_pos))

        for connect in self.map.connects:
            start_pos = (
                ((connect.zone1.absc - self.min_x) * self.gap + self.margin),
                ((connect.zone1.ordinate - self.min_y) * self.gap + self.margin)
            )
            end_pos = (
                ((connect.zone2.absc - self.min_x) * self.gap + self.margin),
                ((connect.zone2.ordinate - self.min_y) * self.gap + self.margin)
            )
            py.draw.line(self.screen, connect.color.value, start_pos, end_pos)
        py.display.flip()

        while is_active:
            for event in py.event.get():
                if event.type == py.QUIT :
                    is_active = False
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        is_active = False
            self.clock.tick(60)
        py.quit()

    def drones_launcher(self) -> None:

        for d in self.map.drones:
            pass