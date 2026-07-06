from srcs.models import Zone, StartZone, EndZone, Connection, Drone, DroneState
import pygame as py


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
            self.drones.append(Drone("D{i}", self.start, DroneState.ODE.value))


    def path_finder(self) -> None:
        """Compute, via Dijkstra from 'end', the minimal cost for each zone to reach the end"""
        hub_passed: set[Zone] = set()
        self.end.path_to_end = 0
        remaining = set(self.hubs.values())

        while remaining:
            zone = min(remaining, key=lambda z: z.path_to_end)
            remaining.remove(zone)
            if zone.path_to_end == float("inf"):
                break
            hub_passed.add(zone)

            for neighbor in zone.hubs_connected:
                if neighbor in hub_passed:
                    continue
                new_cost = zone.path_to_end + neighbor.cost
                if new_cost < neighbor.path_to_end:
                    neighbor.path_to_end = new_cost


class MapDisplay():
    def __init__(self, map: Map) -> None:
        self.map = map
        self.initialize_screen()

    def initialize_screen(self) -> None:
        py.init()
        self.screen = py.display.set_mode((2000, 1200))

        is_active = True
        while is_active:
            for event in py.event.get():
                if event.type == py.QUIT :
                    is_active = False
                elif event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        is_active = False

                # if event.type == py.KEYDOWN:
                #     print("Le code généré est le suivant : ")
                #     print("     - event.dict['unicode'] : " + event.dict['unicode'])
                #     print("     - event.key : " + str(event.key))
                #     print("     - py.key.name(event.key) : " + py.key.name(event.key))

        py.quit()


    def drones_launcher(self) -> None:
        for d in self.map.drones:
            pass