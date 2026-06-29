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
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        self.name = name
        self.absc = absc
        self.ordinate = ordinate
        self.max = max_drones
        self.color = color
        self.is_blocked = False
        self.is_restricted = False
        self.is_priority = False


class BlockedZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_blocked = True


class RestrictedZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_restricted = True


class PriorityZone(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)
        self.is_priority = True


class Connection(Zone):
    def __init__(self,
                 name: str,
                 absc: int,
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, absc, ordinate, max_drones, color)