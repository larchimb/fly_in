from enum import Enum


class ParsingError(Exception):
    def __init__(self, indice: int, message: str) -> None:
        self.indice: int = indice + 1
        super().__init__(message)

    def __str__(self) -> str:
        return (f"[PARSING ERROR] line {self.indice}: " + super().__str__())


class DisplayError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return (f"[DISPLAY ERROR]: " + super().__str__())


class MapError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)

    def __str__(self) -> str:
        return (f"[MAP ERROR]: " + super().__str__())


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


class Colors(Enum):
    BLACK = (40, 40, 40)
    RED = (220, 60, 60)
    GREEN = (60, 190, 100)
    YELLOW = (230, 200, 50)
    BLUE = (60, 120, 230)
    MAGENTA = (200, 70, 200)
    CYAN = (70, 200, 200)
    WHITE = (235, 235, 235)


class Zone():
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = Colors.WHITE.name,
                 ) -> None:
        self.name = name
        self.absc = absc
        self.ordinate = ordinate
        self.max = max_drones
        self.cost = 1
        self.drone_in = 0
        self.path_to_end: float = float("inf")
        self.hubs_connected: set[Zone] = set()
        if not color or not color.upper() in [c.name for c in Colors]:
            self.color = Colors.WHITE
        else:
            self.color = Colors[color.upper()]


class StartZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = Colors.GREEN.name,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        if not color or not color.upper() in [c.name for c in Colors]:
            self.color = Colors.GREEN
        else:
            self.color = Colors[color.upper()]


class EndZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = Colors.BLUE.name,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        if not color or not color.upper() in [c.name for c in Colors]:
            self.color = Colors.BLUE
        else:
            self.color = Colors[color.upper()]


class BlockedZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = Colors.RED.name,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_blocked = True

        if not color or not color.upper() in [c.name for c in Colors]:
            self.color = Colors.RED
        else:
            self.color = Colors[color.upper()]


class RestrictedZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = Colors.YELLOW.name,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_restricted = True
        self.cost = 2
        if not color or not color.upper() in [c.name for c in Colors]:
            self.color = Colors.YELLOW
        else:
            self.color = Colors[color.upper()]


class PriorityZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int | None = 1,
                 color: str | None = Colors.MAGENTA.name,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_priority = True
        if not color or not color.upper() in [c.name for c in Colors]:
            self.color = Colors.MAGENTA
        else:
            self.color = Colors[color.upper()]


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
        self.color = Colors.WHITE
        self.co = {zone1.name, zone2.name}
        self.capacity = capacity


class DroneState(Enum):
    ODE = "on_delivery"
    TER = "Terminated"


class Drone():
    def __init__(self,
                 id: str,
                 position: Zone | Connection,
                 state: DroneState = DroneState.ODE,
                 ) -> None:
        self.id = id
        self.pos = position
        self.state = state
        self.moves = 0
        self.path: list[Zone | Connection] = []
        self.path_to_end: int = 0



