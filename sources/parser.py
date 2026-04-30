from enum import Enum
import re
from typing import Any

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
    
    
class HubOptions(Enum):
    COL = "color"
    ZON = "zone"
    MXD = "max_drones"
    
    
class ZoneTypes(Enum):
    NOR = "normal"
    BLO = "blocked"
    RES = "restricted"
    PRI = "priority"


class Parser():
    def __init__(self) -> None:
        self.rows: list[str] = []
        self.hub_names: list[str] =[]
        self.connection_names: list[set[str, str]] = []
        self.dic: dict[str, dict[Any, Any]] = {}
        self.nb_starts = 0
        self.nb_ends = 0

    def check_file(self, file: str) -> None:
        """Check all conditions for entry's file"""
        try:
            text: str = open(file).read()
        except (FileNotFoundError, Exception) as e:
            raise (e)
        self.delete_comments(text)
        if not self.rows:
            raise Exception(f" {file} is empty or contain comments only")
        
        self.check_drones()
        for self.i in range(self.index + 1, len(self.rows)):
            if self.rows[self.i]:
                self.check_line(self.rows[self.i])
        if self.nb_starts == 0:
            raise Exception("There is no start point")
        if self.nb_ends == 0:
            raise Exception("There is no end point") 
            # print(self.rows)

    def delete_comments(self, string: str) -> None:
        """Delete all comments part in the file"""
        all_rows = string.splitlines()
        for row in all_rows:
            line = row.strip()
            for letter in line:
                if letter == "#":
                    index = line.index(letter)
                    line = line[:index]
                    break
            self.rows.append(line)

    def check_drones(self) -> None:
        ("""Find the first no empty line and 
        check if the number of drone is positive.""")
        self.index: int = next((i for i, row in enumerate(self.rows) if row))
        key, _, value = self.rows[self.index].strip().partition(": ")

        if not key.strip() == "nb_drones":
            raise ParsingError(self.index,
                             "\nFirst line must be: 'nb_drones: {positive int}'\n"
                             f"You have: '{key.strip() + _ + value}'")
        try:
            value = int(value.strip())
            if value <= 0:
                raise ValueError
        except ValueError:
            raise ParsingError(self.index,
                f"value = {value}: "
                "You must have a positive number of drone"
                )

    def check_line(self, line: str) -> None:
        """Check if datas in the line are correctly writted"""
        if not line:
            return
        key, _, rest_line = line.strip().partition(": ")
        if key in HubTypes:
            if key == HubTypes.STR.value:
                self.nb_starts += 1
            elif key == HubTypes.END.value:
                self.nb_ends += 1
            elif key == "nb_drones":
                raise ParsingError(self.i, "nb_drones is already set")
            if self.nb_starts > 1:
                raise ParsingError(self.i, "There is too many start points")
            if self.nb_ends > 1:
                raise ParsingError(self.i, "There is too many end points")
            self.check_hub(rest_line)
        elif key == "connection":
            self.check_connection(rest_line)
        else:
            raise ParsingError(self.i, f"'{key}' is unknown, "
                               f"it must be a 'hub', 'start_hub', 'end_hub' or a 'connection'")
            
    def check_hub(self, line: str) -> None:
        """Check hub's name, coordinates and options"""
        match = re.search(r"\[(.*?)\]", line)
        options = []
        if match:
            options = match.group(1).strip().split(" ")
            options = list(filter(None, options))
            elements = (line[:line.index('[')]).strip().split(" ")
        else:
            elements = line.strip().split()
        elements = list(filter(None, elements)) 
        try:
            name, abscissa, ordinate = elements
        except Exception:
            raise ParsingError(self.i, "You must have 3 parameters before options '[]'")
        
        if not name.find("-") == -1:
            raise ParsingError(self.i, "Hub's name must not contain '-'")
        try:
            abscissa = int(abscissa)
            ordinate = int(ordinate)
        except Exception:
            raise ParsingError(self.i, "Coordinates must be integers")
        if name in self.hub_names:
            raise ParsingError(self.i, f"There is already a '{name}' hub.")
        self.hub_names.append(name)
        if options:
            self.check_hub_options(options)
        print(options)
        
    def check_hub_options(self, options: list[str]) -> None:
        if len(options) > 3:
            raise ParsingError(self.i, "too many options, max 3")
        color_key = 0
        zone_key = 0
        max_key = 0
        for option in options:
            try:
                key, value = option.split("=")
            except Exception:
                raise ParsingError(self.i, "options must be written:[color=blue max_drones=2]")  
            if not key in HubOptions:
                raise ParsingError(self.i, 
                                   f"'{key}', options availables are 'color', 'zone' and 'max_drones'")
            elif key == HubOptions.COL.value:
                color_key += 1
                if not value.isalpha():
                    raise ParsingError(self.i, "color must be an alphabetic string")
            elif key == HubOptions.ZON.value:
                zone_key += 1
                if not value in ZoneTypes:
                    raise ParsingError(self.i,
                                       f"'{value}', options availables are 'normal', "
                                       "'blocked', 'restricted' and 'priority'")
            elif key == HubOptions.MXD.value:
                max_key += 1
                try:
                    value = int(value)
                    if value < 0:
                        raise ParsingError
                except Exception:
                    raise ParsingError(self.i, "max_drones must be a positive integer")  
                
            if color_key > 1 or zone_key > 1 or max_key > 1:
                raise ParsingError(self.i, "put each option once")
                    
                
    def check_connection(self, line: str) -> None:
        pass


if __name__ == "__main__":
    try:
        parser = Parser()
        parser.check_file("test.txt")
    except (ParsingError, Exception) as e:
        print(e)