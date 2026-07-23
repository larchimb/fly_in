from srcs.models import MapError, Zone, StartZone, EndZone, RestrictedZone, BlockedZone, PriorityZone, Connection, Drone, Colors, DisplayError
import pygame as py
import sys
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
        self.connects = frozenset(connections)
        self.drones: list[Drone] = self.create_drones_list(nb_drones)
        self.arrived_drones: list[Drone] = []
        self.path_for_hub()
        self.turn_moved = 0
        self.total_moved = 0
        self.path_finder()


    def create_drones_list(self, nb_drones: int) -> list[Drone]:
        """Create the drones list"""
        drones = []
        for i in range(1, nb_drones + 1):
            d = Drone(f"D{i}", self.start)
            drones.append(d)
            d.path.append(self.start)
            self.start.drone_in += 1
        return drones

    def path_for_hub(self) -> None:
        """Compute, via Dijkstra from 'end', the minimal cost for each zone to reach the end"""
        hub_passed: set[Zone] = set()
        self.end.path = 0
        remaining = set(self.hubs.values())
        while remaining:
            zone = min(remaining, key=lambda z: z.path)
            remaining.remove(zone)
            if zone.path == float("inf"):
                break
            hub_passed.add(zone)

            for neighbor in zone.hubs_connected:
                if neighbor in hub_passed:
                    continue
                if isinstance(neighbor, BlockedZone):
                    remaining.remove(neighbor)
                    hub_passed.add(neighbor)
                    continue

                new_cost = zone.path + neighbor.cost
                if new_cost < neighbor.path:
                    neighbor.path = new_cost
        if self.start.path == float("inf"):
            raise Exception("there is no path from start to end")

    def path_finder(self) -> None:
        """Find the fastest path to the end for each drone"""
        self.turn = 0
        while len(self.drones) - len(self.arrived_drones) > 0:
            self.turn += 1
            self.turn_moved = 0
            for d in self.drones:
                if d.pos == self.end:
                    continue
                targets = []
                self.start.path = min(self.start.hubs_connected, key=lambda z: z.path).path + 1
                actual = d.pos
                neighbors = list(actual.hubs_connected)
                for z in neighbors:
                    if ((z in d.path) or
                        (isinstance(z, PriorityZone)
                            and actual.path < z.path)):
                        continue
                    else:
                        targets.append(z)

                p_list = [t for t in targets if isinstance(t, PriorityZone)]

                if isinstance(d.pos, Connection):
                    target = self.hubs[(d.pos.co - {d.path[-2].name}).pop()]
                elif p_list:
                    target = self.pick_target(p_list, actual)
                else:
                    target = self.pick_target(targets, actual)

                self.register_path(d, target)
                if target:
                    actual = target
                    self.turn_moved += 1
                    self.total_moved += 1

                if target == self.end:
                    self.arrived_drones.append(d)

            self.clean_co()

    def pick_target(self,
                        targets: list[Zone] | list[PriorityZone],
                        actual: Zone) -> Zone | None:
            """Find the closest free hub to the end"""
            targets = [t for t in targets if t.path <= actual.path]
            if not targets:
                return None
            for zone in sorted(targets, key=lambda z: z.path):
                if (zone.capacity and
                    zone.capacity > zone.drone_in):
                    for c in self.connects:
                        if (c.co == {actual.name, zone.name}
                            and c.drones_passed < c.capacity):
                            c.drones_passed += 1
                            actual.drone_in -= 1
                            zone.drone_in += 1

                            if isinstance(zone, RestrictedZone):
                                return c
                            return zone
                else:
                    zone.path += 1
            return None

    def register_path(self, d: Drone, target: Zone | None) -> None:
        """Register the step of the path in the drone"""
        if target is None:
            d.path.append(d.path[-1])
        else:
            d.path.append(target)


    def clean_co(self) -> None:
        for c in self.connects:
            if c in [d.pos for d in self.drones]:
                continue
            else:
                c.drones_passed = 0


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
        width_rec = 6 * (self.gap + self.hub_radius)

        if self.width < width_rec:
            self.width = width_rec + 20
        self.height = (
            (self.max_y - self.min_y) * self.gap + 2 * self.margin + self.legend
            )
        self.size = (self.width, self.height)
        if self.width > 3500:
            print(self.width)
            raise DisplayError("Width is too large for this map")
        if self.height > 2000:
            print(self.height)
            raise DisplayError("Height is too high for this map")

    def initialize_screen(self) -> None:
        """Initialize the empty screen"""
        self.screen = py.display.set_mode(self.size)
        py.display.set_caption("Fly_in")
        self.draw_static()
        py.display.flip()
        self.launch_animation()

    def draw_static(self) -> None:
        """Draw hubs, connections and legend (static background)"""
        self.screen.fill(Colors.WHITE.value)
        for hub in self.map.hubs.values():
            x, y = self.zone_pos(hub)
            py.draw.circle(
                self.screen, hub.color.value, (x, y), self.hub_radius
                )
            self.draw_label(hub.name, Colors.BLACK, x, y + self.hub_radius + 12)

        for connect in self.map.connects:
            start_pos = self.zone_pos(connect.zone1)
            end_pos = self.zone_pos(connect.zone2)
            py.draw.line(self.screen, connect.color.value, start_pos, end_pos, 4)
        self.draw_legend()

    def draw_legend(self) -> None:
        """Draw the legend on the screen"""
        height_rec = 112
        width_rec = 6 * (self.gap + self.hub_radius)
        x_legend = (self.width - width_rec) / 2
        y_legend = self.height - self.legend
        x = x_legend + self.gap
        y = y_legend + 50
        place = (x, y)
        rectangle = py.Rect(
            x_legend,
            y_legend,
            width_rec,
            height_rec
        )
        py.draw.rect(self.screen, Colors.BLACK.value, rectangle, 5)
        py.draw.circle(self.screen, Colors.BLACK.value, place, self.hub_radius)
        y_label = y + self.hub_radius + 12
        self.draw_label("Classic Zone", Colors.BLACK, x, y_label)
        for c in Zone.__subclasses__():
            if c is Connection:
                break
            x += self.gap
            zone = c(c.__name__, x, y)
            py.draw.circle(
                self.screen, zone.color.value, (x, y), self.hub_radius
                )
            self.draw_label(zone.name, zone.color, x, y_label)

    def draw_label(self,
                   name: str,
                   color: Colors,
                   x: float,
                   y: float) -> None:
        """Draw the label of a zone under itself"""
        label = self.font.render(name, True, color.value)
        label_pos = (x, y)
        self.screen.blit(label, label.get_rect(center=label_pos))

    def zone_pos(self, zone: Zone) -> tuple[float, float]:
        """Compute the pixel position of a zone on screen"""
        x = (zone.absc - self.min_x) * self.gap + self.margin
        y = (zone.ordinate - self.min_y) * self.gap + self.margin
        return (x, y)

    def launch_animation(self) -> None:
        is_active = True
        while is_active:
            for event in py.event.get():
                if event.type == py.QUIT :
                    is_active = False
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        is_active = False
            # self.drones_launcher()
            self.clock.tick(60)
        py.quit()

    def drones_launcher(self) -> None:
        """Make the drones advance on the map"""
        for d in self.map.drones:
            actual = d.pos
            neighbors = [
                t for t in d.pos.hubs_connected
                if not isinstance(t, BlockedZone)
                ]
            p_list = [t for t in neighbors if isinstance(t, PriorityZone)]
            if p_list:
                target = self.pick_target(p_list, actual)
            else:
                target = self.pick_target(neighbors, actual)
            if target is None:
                continue
            else:
                self.move_drone(d, actual, target)
            neighbors = []
            p_list = []

    def pick_target(self,
                    targets: list[Zone] | list[PriorityZone],
                    actual: Zone) -> Zone | None:
        """Find the closest free hub to the end"""
        targets = [t for t in targets if t.path < actual.path]
        if not targets:
            return None
        for zone in sorted(targets, key=lambda z: z.path):
            if (zone.capacity and
                zone.capacity > zone.drone_in):
                for c in self.map.connects:
                    if (c.co == {actual.name, zone.name}
                        and c.drones_passed < c.capacity):
                        c.drones_passed += 1
                        actual.drone_in -= 1
                        zone.drone_in += 1
                        return zone
        return None

    def move_drone(self, drone: Drone, start: Zone, goal: Zone) -> None:
        """Animate a drone moving from a zone to another one"""
        x_start, y_start = self.zone_pos(start)
        x_goal, y_goal = self.zone_pos(goal)
        steps = 30

        for i in range(1, steps + 1):
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    sys.exit()

            t = i / steps
            x = x_start + (x_goal - x_start) * t
            y = y_start + (y_goal - y_start) * t

            self.draw_static()
            py.draw.circle(self.screen, Colors.CYAN.value, (x, y), self.drone_radius)
            self.draw_label(drone.id, Colors.BLACK, x, y)
            py.display.flip()
            self.clock.tick(60)

        drone.pos = goal
        drone.moves += 1
        if drone.pos == self.map.end:
            self.map.drones.remove(drone)
        print(f"{drone.id}-{drone.pos.name}")
