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
                 abs: int, 
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        self.name = name
        self.abs = abs
        self.ordinate = ordinate
        self.max = max_drones
        self.color = color
        

class BlockedZone(Zone):
    def __init__(self, 
                 name: str, 
                 abs: int, 
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, abs, ordinate, max_drones, color)
        

class RestrictedZone(Zone):
    def __init__(self, 
                 name: str, 
                 abs: int, 
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, abs, ordinate, max_drones, color)


class PriorityZone(Zone):
    def __init__(self, 
                 name: str, 
                 abs: int, 
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, abs, ordinate, max_drones, color)
        
    
class Connection():
    def __init__(self, 
                 name: str, 
                 abs: int, 
                 ordinate: int,
                 max_drones: int = 1,
                 color: str | None = None,
                 ) -> None:
        super().__init__(name, abs, ordinate, max_drones, color)