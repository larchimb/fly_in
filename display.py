from models import (
    MapError,
    Zone,
    StartZone,
    EndZone,
    BlockedZone,
    RestrictedZone,
    PriorityZone,
    Connection,
    Drone,
    Colors,
    DisplayError,
)
import pygame as py
import sys


class Map:
    def __init__(
        self,
        start: StartZone | Zone,
        end: EndZone | Zone,
        hubs: dict[str, Zone],
        connections: list[Connection],
        nb_drones: int,
    ) -> None:
        self.start = start
        self.end = end
        self.hubs = hubs
        self.connects = frozenset(connections)
        self.drones: list[Drone] = self.create_drones_list(nb_drones)
        self.arrived_drones: list[Drone] = []
        self.path_for_hub()
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
        """Compute, via Dijkstra from 'end',
        the minimal cost for each zone to reach the end"""
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
                new_cost = zone.path + neighbor.cost
                if new_cost < neighbor.path:
                    neighbor.path = new_cost
        if self.start.path == float("inf"):
            raise MapError("there is no path from start to end")

    def path_finder(self) -> None:
        """Find the fastest path to the end for each drone"""
        self.turn = 0
        while len(self.drones) - len(self.arrived_drones) > 0:
            self.turn += 1
            for d in self.drones:
                targets = list(d.pos.hubs_connected)
                target = self.pick_target(d, targets, d.pos)

                self.register_path(d, target)
                if target == self.end:
                    self.arrived_drones.append(d)

            self.clean_co()

    def pick_target(
        self,
        d: Drone,
        neighbors: list[Zone] | list[PriorityZone],
        actual: Zone,
    ) -> Zone | None:
        """Find the closest free hub to the end"""
        if isinstance(d.pos, Connection):
            return self.hubs[(d.pos.co - {d.path[-2].name}).pop()]

        targs = [
            t for t in neighbors if (t.path <= actual.path and t not in d.path)
        ]
        if not targs:
            return None

        targets = sorted(
            targs, key=lambda z: (not isinstance(z, PriorityZone), z.path)
        )

        for zone in targets:
            if zone.capacity and zone.capacity > zone.drone_in:
                for c in self.connects:
                    if (
                        c.co == {actual.name, zone.name}
                        and c.drones_passed < c.capacity
                    ):
                        c.drones_passed += 1
                        actual.drone_in -= 1
                        zone.drone_in += 1
                        if isinstance(zone, RestrictedZone):
                            return c
                        return zone
        return None

    def register_path(self, d: Drone, target: Zone | None) -> None:
        """Register the step of the path in the drone"""
        if target is None:
            d.path.append(d.path[-1])
        else:
            d.path.append(target)
            d.pos = target
            self.total_moved += 1
            d.moves += 1

    def clean_co(self) -> None:
        for c in self.connects:
            if c in [d.pos for d in self.drones]:
                continue
            else:
                c.drones_passed = 0


class MapDisplay:
    """Static pygame view of a Map: colored hub nodes, connections, legend."""

    def __init__(self, map: Map) -> None:
        self.mapping = map
        self.turn_moved = 0
        self.total_moved = 0
        self.d_moved = 0
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
        self.paused = False

        abscissas = [z.absc for z in self.mapping.hubs.values()]
        ordinates = [z.ordinate for z in self.mapping.hubs.values()]
        self.min_x = min(abscissas)
        self.max_x = max(abscissas)
        self.min_y = min(ordinates)
        self.max_y = max(ordinates)

        self.width = (self.max_x - self.min_x) * self.gap + 2 * self.margin
        width_rec = 6 * (self.gap + self.hub_radius)

        if self.width < width_rec:
            self.width = width_rec + 20
        self.height = (
            (self.max_y - self.min_y) * self.gap
            + 2 * self.margin
            + self.legend
        )
        self.size = (self.width, self.height)
        if self.width > 3650:
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
        for hub in self.mapping.hubs.values():
            x, y = self.zone_pos(hub)
            py.draw.circle(
                self.screen, hub.color.value, (x, y), self.hub_radius
            )
            self.draw_label(
                hub.name, Colors.BLACK, x, y + self.hub_radius + 12
            )

        for connect in self.mapping.connects:
            start_pos = self.zone_pos(connect.zone1)
            end_pos = self.zone_pos(connect.zone2)
            x, y = self.zone_pos(connect)
            py.draw.line(
                self.screen, connect.color.value, start_pos, end_pos, 4
            )
            self.draw_label(
                connect.name, Colors.BLACK, x, y - 10
                        )
        self.draw_legend()
        self.draw_infos()

    def draw_infos(self) -> None:
        """Draw board's template """
        width_rec = 200
        height_rec = 110
        x_rec = (self.width - width_rec - 50)
        y_rec = 30
        self.x_turn = x_rec + 10
        self.y_turn = y_rec + 10
        rectangle = py.Rect(x_rec, y_rec, width_rec, height_rec)
        py.draw.rect(self.screen, Colors.BLACK.value, rectangle, 5)
        self.draw_text("Turn:", Colors.BLACK, self.x_turn, self.y_turn)
        self.draw_text(
            "Total moved:", Colors.BLACK, self.x_turn, self.y_turn + 20
            )
        self.draw_text(
            "Turn moved:", Colors.BLACK, self.x_turn, self.y_turn + 40
            )
        self.draw_text(
            "Average:", Colors.BLACK, self.x_turn, self.y_turn + 60
            )

    def draw_legend(self) -> None:
        """Draw the legend on the screen"""
        height_rec = 112
        width_rec = 6 * (self.gap + self.hub_radius)
        x_legend = (self.width - width_rec) / 2
        y_legend = self.height - self.legend
        x = x_legend + self.gap
        y = y_legend + 50
        rectangle = py.Rect(x_legend, y_legend, width_rec, height_rec)
        py.draw.rect(self.screen, Colors.BLACK.value, rectangle, 5)

        zones = [
            Zone, StartZone, EndZone, BlockedZone, PriorityZone, RestrictedZone
            ]
        y_label = y + self.hub_radius + 12
        for z in zones:
            zone = z(z.__name__, x, y)
            py.draw.circle(
                self.screen, zone.color.value, (x, y), self.hub_radius
            )
            self.draw_label(zone.name, zone.color, x, y_label)
            x += self.gap

    def draw_label(self, name: str, color: Colors, x: float, y: float) -> None:
        """Draw the label of a zone under itself"""
        label = self.font.render(name, True, color.value)
        label_pos = (x, y)
        self.screen.blit(label, label.get_rect(center=label_pos))

    def draw_text(self, name: str, color: Colors, x: float, y: float) -> None:
        """Draw the label of a zone under itself"""
        label = self.font.render(name, True, color.value)
        label_pos = (x, y)
        self.screen.blit(label, label_pos)

    def actualise_infos(self, i: int) -> None:
        """To refresh board's informations"""
        # rec =
        self.draw_text(
            f"{i}", Colors.BLACK, self.x_turn + 90, self.y_turn
            )
        self.draw_text(
            f"{self.total_moved}", Colors.BLACK,
            self.x_turn + 90,
            self.y_turn + 20
            )
        self.draw_text(
                    f"{self.d_moved}", Colors.BLACK,
                    self.x_turn + 90,
                    self.y_turn + 40
                    )

    def zone_pos(self, zone: Zone) -> tuple[float, float]:
        """Compute the pixel position of a zone on screen"""
        x = (zone.absc - self.min_x) * self.gap + self.margin
        y = (zone.ordinate - self.min_y) * self.gap + self.margin
        return (x, y)

    def terminal_output(self, i: int) -> None:
        """Print the moves of the turn on the terminal"""
        output = ""
        for d in self.mapping.drones:
            if d.path[i] != self.mapping.end and d.path[i] != d.path[i + 1]:
                output += f"{d.id}-{d.path[i + 1].name} "
        print(output)

    def average_d_(self) -> None:
        """To display the average turn by drone"""
        drones_moves = [d.moves for d in self.mapping.drones]
        average = sum(drones_moves) / len(drones_moves)
        self.draw_text(
                f"{average:.2f}", Colors.BLACK,
                self.x_turn + 90,
                self.y_turn + 60
                )
        py.display.flip()

    def launch_animation(self) -> None:
        """Animate every turn of the simulation."""
        for i in range(0, self.mapping.turn):
            self.d_moved = 0
            if not self.move_turn(i):
                py.quit()
                sys.exit()
            self.terminal_output(i)
            py.time.wait(300)
        self.average_d_()
        while 1:
            for event in py.event.get():
                if (
                    event.type == py.QUIT
                    or event.type == py.KEYDOWN
                    and event.key == py.K_ESCAPE
                ):
                    py.quit()
                    sys.exit()

    def move_turn(self, i: int) -> bool:
        """Animate all drone for one turn"""
        steps = 40
        step = 1
        for d in self.mapping.drones:
            if d.path[i] != self.mapping.end and d.path[i] != d.path[i + 1]:
                self.d_moved += 1

        while step <= steps:
            for event in py.event.get():
                if (
                    event.type == py.QUIT
                    or event.type == py.KEYDOWN
                    and event.key == py.K_ESCAPE
                ):
                    return False
                elif event.type == py.KEYDOWN and event.key == py.K_SPACE:
                    self.paused = not self.paused
            t = step / steps
            self.draw_static()
            for d in self.mapping.drones:
                x_start, y_start = self.zone_pos(d.path[i])
                if (d.path[i] == self.mapping.end or
                        d.path[i] == d.path[i + 1]):
                    self.draw_drone(d, x_start, y_start)
                else:
                    x_goal, y_goal = self.zone_pos(d.path[i + 1])
                    x = x_start + (x_goal - x_start) * t
                    y = y_start + (y_goal - y_start) * t
                    self.draw_drone(d, x, y)
                    self.total_moved += int(1 * t)
            self.actualise_infos(i + 1)
            py.display.flip()
            self.clock.tick(60)

            if not self.paused:
                step += 1
        return True

    def draw_drone(self, d: Drone, x: float, y: float) -> None:
        """Drawing a drone at placement (x, y)"""
        py.draw.circle(
            self.screen, Colors.CYAN.value, (x, y), self.drone_radius
        )
        self.draw_label(d.id, Colors.BLACK, x, y)
