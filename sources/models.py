from enum import Enum
from abc import abstractmethod, ABC


class ParsingError(Exception):
    def __init__(self, indice: int, message: str) -> None:
        self.indice: int = indice + 1
        super().__init__(message)

    def __str__(self) -> str:
        return (f"[PARSING ERROR] line {self.indice}: " + super().__str__())


class HubTypes(Enum):
    STR = "start_hub"
    END = "end_hub"
    HUB = "hub"
    CON = "connection"


class HubOptions(Enum):
    COL = "color"
    ZON = "zone"
    MXD = "max_drones"


class ConnectionOptions(Enum):
    CAP = "max_link_capacity"


class ZoneTypes(Enum):
    NOR = "normal"
    BLO = "blocked"
    RES = "restricted"
    PRI = "priority"


class Zone():
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = None,
                 ) -> None:
        self.name = name
        self.absc = absc
        self.ordinate = ordinate
        self.max = max_drones
        self.color = color
        self.cost = 1
        self.path_to_end: float = float("inf")
        self.hubs_connected: set[Zone] = set()


class StartZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)


class EndZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)


class BlockedZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_blocked = True


class RestrictedZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_restricted = True
        self.cost = 2


class PriorityZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_priority = True


class Connection():
    def __init__(self,
                 name: str,
                 zone1: Zone,
                 zone2: Zone,
                 capacity: int = 1
                 ) -> None:
        self.name = name
        self.zone1 = zone1
        self.zone2 = zone2
        self.co = {zone1.name, zone2.name}
        self.capacity = capacity


class DroneState(Enum):
    ODE = "on_delivery"
    TER = "Terminated"


class Drone():
    def __init__(self,
                 id: str,
                 position: Zone | Connection,
                 state: str,
                 ) -> None:
        self.id = id
        self.pos = position
        self.state = state
        self.moves = 0
        self.path: list[Zone | Connection] = []
        self.path_to_end: int = 0


class Map():
    def __init__(self,
                 start: StartZone | Zone,
                 end: EndZone | Zone,
                 hubs: dict[str,Zone],
                 connections: list[Connection],
                 nb_drones: int) -> None:
        self.start = start
        self.end = end
        self.hubs = hubs
        self.connects = connections
        self.drones: list[Drone] = []
        self.create_drones_list(nb_drones)
        self.turn_moved = 0
        self.total_moved = 0

    def create_drones_list(self, nb_drones: int) -> None:
        for i in range(1, nb_drones + 1):
            self.drones.append(Drone("D{i}", self.start, DroneState.ODE.value))

    def path_finder(self) -> None:
        """Compute, via Dijkstra from 'end', the minimal cost for each zone to reach the end"""
        hub_passed: set[Zone] = set()
        self.hubs["end"].path_to_end = 0
        remaining = set(self.hubs.values())

        while remaining:
            zone = min(remaining, key=lambda z: z.path_to_end)
            remaining.remove(zone)
            if zone.path_to_end == float("inf"):
                break
            hub_passed.add(zone)


