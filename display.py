from models import (
    Zone,
    StartZone,
    EndZone,
    BlockedZone,
    RestrictedZone,
    PriorityZone,
    Connection,
    Colors,
    Drone,
    DisplayError,
)
from map_builder import Map
import pygame as py
import sys


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
        self.background = py.Surface(self.size)
        self.draw_static()
        self.screen.blit(self.background, (0, 0))
        py.display.flip()
        self.launch_animation()

    def draw_static(self) -> None:
        """Draw hubs, connections and legend once onto the background"""
        self.background.fill(Colors.WHITE.value)
        for hub in self.mapping.hubs.values():
            x, y = self.zone_pos(hub)
            py.draw.circle(
                self.background, hub.color.value, (x, y), self.hub_radius
            )
            self.draw_label(
                hub.name, Colors.BLACK, x, y + self.hub_radius + 12,
                self.background
            )

        for connect in self.mapping.connects:
            start_pos = self.zone_pos(connect.zone1)
            end_pos = self.zone_pos(connect.zone2)
            x, y = self.zone_pos(connect)
            py.draw.line(
                self.background, connect.color.value, start_pos, end_pos, 4
            )
            self.draw_label(
                connect.name, Colors.BLACK, x, y - 10, self.background
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
        py.draw.rect(self.background, Colors.BLACK.value, rectangle, 5)
        self.draw_text("Turn:", Colors.BLACK, self.x_turn, self.y_turn)
        self.draw_text(
            "Total moved:", Colors.BLACK, self.x_turn, self.y_turn + 20,
            self.background
            )
        self.draw_text(
            "Turn moved:", Colors.BLACK, self.x_turn, self.y_turn + 40,
            self.background
            )
        self.draw_text(
            "Average:", Colors.BLACK, self.x_turn, self.y_turn + 60,
            self.background
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
        py.draw.rect(self.background, Colors.BLACK.value, rectangle, 5)

        zones = [
            Zone, StartZone, EndZone, BlockedZone, PriorityZone, RestrictedZone
            ]
        y_label = y + self.hub_radius + 12
        for z in zones:
            zone = z(z.__name__, x, y)
            py.draw.circle(
                self.background, zone.color.value, (x, y), self.hub_radius
            )
            self.draw_label(zone.name, zone.color, x, y_label, self.background)
            x += self.gap

    def draw_label(self,
                   name: str,
                   color: Colors,
                   x: float,
                   y: float,
                   surface: py.Surface | None = None) -> None:
        """Draw the label of a zone under itself"""
        target = surface if surface is not None else self.screen
        label = self.font.render(name, True, color.value)
        label_pos = (x, y)
        target.blit(label, label.get_rect(center=label_pos))

    def draw_text(self,
                  name: str,
                  color: Colors,
                  x: float,
                  y: float,
                  surface: py.Surface | None = None) -> None:
        """Draw the label of a zone under itself"""
        target = surface if surface is not None else self.screen
        label = self.font.render(name, True, color.value)
        label_pos = (x, y)
        target.blit(label, label_pos)

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

    def hubs_upgrade(self, i: int) -> None:
        """Upgrade hub's capacity"""
        for d in self.mapping.drones:
            if isinstance(d.path[i + 1], Connection):
                d.path[i].drone_in -= 1
                d.path[i + 2].drone_in += 1
            elif isinstance(d.path[i], Connection):
                continue
            else:
                d.path[i].drone_in -= 1
                d.path[i + 1].drone_in += 1

    def launch_animation(self) -> None:
        """Animate every turn of the simulation."""
        for i in range(0, self.mapping.turn):
            self.d_moved = 0
            if not self.move_turn(i):
                py.quit()
                sys.exit()
            self.hubs_upgrade(i)
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
        steps = 60
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
            self.screen.blit(self.background, (0, 0))
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
