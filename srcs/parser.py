from srcs.models import ParsingError, HubTypes, HubOptions, ZoneTypes, Zone
from srcs.models import StartZone, EndZone, BlockedZone, RestrictedZone, PriorityZone
from srcs.models import ConnectionOptions, Connection
from srcs.display import Map
import re
from typing import Any


class Parser():
    def __init__(self) -> None:
        self.rows: list[str] = []
        self.hubs: dict[str, Zone | StartZone | EndZone] = {}
        self.connections: list[Connection] = []
        self.nb_connect = 0
        self.nb_starts = 0
        self.nb_ends = 0
        self.drones = 0

    def check_file(self, file: str) -> None:
        """Check all conditions for entry's file"""
        try:
            with open(file) as f:
                text: str = f.read()
        except FileNotFoundError as e:
            raise (e)
        # To catch other errors (permission, folder instead of file)
        except OSError as e:
            raise Exception(f"Unable to read file '{file}': {e}") from e
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
            int_value = int(value.strip())
            if int_value <= 0:
                raise ValueError
        except ValueError:
            raise ParsingError(self.index,
                f"value = {value}: "
                "You must have a positive number of drone"
                )
        self.drones = int_value

    def check_line(self, line: str) -> None:
        """Check if datas in the line are correctly writted"""
        self.is_start = False
        self.is_end = False
        if not line:
            return
        key, _, rest_line = line.strip().partition(": ")
        if key not in [e.value for e in HubTypes]:
            raise ParsingError(self.i, f"'{key}' is unknown, "
                               f"it must be a 'hub', 'start_hub', 'end_hub' or a 'connection'")
        elif key == "nb_drones":
            raise ParsingError(self.i, "nb_drones is already set")
        elif key == "connection":
            self.check_connection(rest_line)
        else:
            if key == HubTypes.STR.value:
                self.nb_starts += 1
                if self.nb_starts > 1:
                    raise ParsingError(self.i, "There is too many start points")
                self.is_start = True
            elif key == HubTypes.END.value:
                self.nb_ends += 1
                if self.nb_ends > 1:
                    raise ParsingError(self.i, "There is too many end points")
                self.is_end = True
            self.check_hub(rest_line)

    def check_hub(self, line: str) -> None:
        """Check hub's name, coordinates and options"""
        matches = re.findall(r"\[.*?\]", line)
        options = []
        if matches and line.index(']') != len(line.strip()) - 1:
            raise ParsingError(self.i, "No text allowed after options block '[]'")
        if matches:
            options = matches[0][1:-1].strip().split()
            elements = (line[:line.index('[')]).strip().split()
        else:
            elements = line.strip().split()
        try:
            name, abscissa, ordinate = elements
        except Exception:
            raise ParsingError(self.i, "You must have 3 parameters before options '[]'")

        if not name.find("-") == -1:
            raise ParsingError(self.i, "Hub's name must not contain '-'")
        try:
            int_abscissa = int(abscissa)
            int_ordinate = int(ordinate)
        except Exception:
            raise ParsingError(self.i, "Coordinates must be integers")
        if name in self.hubs.keys():
            raise ParsingError(self.i, f"There is already a '{name}' hub.")
        for hub in self.hubs.keys():
            if (int_abscissa == self.hubs[hub].absc
            and int_ordinate == self.hubs[hub].ordinate):
                raise ParsingError(self.i, f"There is already a hub to this coordinates.")
        parsed_options = {}
        if options:
            parsed_options = self.check_hub_options(options)
        self.add_hub(name, int_abscissa, int_ordinate, parsed_options)

    def check_hub_options(self, options: list[str]) -> dict[str, str | int]:
        dic_option = {}
        if len(options) > 3:
            raise ParsingError(self.i, "too many options, max 3")
        max_key = 0
        color_key = 0
        zone_key = 0
        for option in options:
            try:
                key, value = option.split("=")
            except Exception:
                raise ParsingError(self.i, "options must be written:[color=blue max_drones=2]")
            if key not in [e.value for e in HubOptions]:
                raise ParsingError(self.i,
                                   f"'{key}', options availables are 'color', 'zone' and 'max_drones'")
            elif key == HubOptions.COL.value:
                color_key += 1
                dic_option[key] = value
                if not value.isalpha():
                    raise ParsingError(self.i, "color must be an alphabetic string")
            elif key == HubOptions.ZON.value:
                zone_key += 1
                dic_option[key] = value
                if value not in [e.value for e in ZoneTypes]:
                    raise ParsingError(self.i,
                                       f"'{value}', options availables are 'normal', "
                                       "'blocked', 'restricted' and 'priority'")
            elif key == HubOptions.MXD.value:
                max_key += 1
                try:
                    int_value = int(value)
                    if int_value <= 0:
                        raise ParsingError(self.i, "max_drones must be a positive integer")
                    dic_option[key] = int_value
                except Exception:
                    raise ParsingError(self.i, "max_drones must be a positive integer")

            if color_key > 1 or zone_key > 1 or max_key > 1:
                raise ParsingError(self.i, "put each option once")
        return dic_option

    def add_hub(self, name: str, absc: int, ord: int, dic_option: dict[str, Any]) -> None:
        """Add the hub to the dictionnary with the good specification"""
        color: str | None = None
        max_drone: int | None = 1
        zone: str | None = None
        if dic_option:
            color = dic_option.get("color")
            max_drone = dic_option.get(HubOptions.MXD.value)
            zone = dic_option.get(HubOptions.ZON.value)

        if self.is_start:
            self.hubs[name] = StartZone(name, absc, ord, self.drones, color)
        elif self.is_end:
            self.hubs[name] = EndZone(name, absc, ord, self.drones, color)
        elif zone == ZoneTypes.BLO.value:
            self.hubs[name] = BlockedZone(name, absc, ord, max_drone, color)
        elif zone == ZoneTypes.RES.value:
            self.hubs[name] = RestrictedZone(name, absc, ord, max_drone, color)
        elif zone == ZoneTypes.PRI.value:
            self.hubs[name] = PriorityZone(name, absc, ord, max_drone, color)
        else:
            self.hubs[name] = Zone(name, absc, ord, max_drone, color)
        print([self.hubs[name].name,self.hubs[name].color])

    def check_connection(self, line: str) -> None:
        """Check connection's name, coordinates and options"""
        matches = re.findall(r"\[.*?\]", line)
        capacity: int | None = 1
        if matches and line.index(']') != len(line.strip()) - 1:
            raise ParsingError(self.i, "No text allowed after options block '[]'")
        if matches:
            capacity = self.check_connect_options(matches)
            zones = (line[:line.index('[')]).strip().split("-")
        else:
            zones = line.strip().split("-")
        if len(zones) != 2:
            raise ParsingError(self.i, "connection must follow 'zone1-zone2' model")
        zone1 = zones[0]
        zone2 = zones[1]
        pair = {zone1, zone2}
        if not all(e in self.hubs for e in [zone1, zone2]):
            raise ParsingError(self.i, "one of the zone isn't define")
        if zone1 == zone2:
            raise ParsingError(self.i, "a connection must be beetween 2 differentes zones")
        if any(pair == c.co for c in self.connections):
            raise ParsingError(self.i, "There is already this connection")
        name = HubTypes.CON.value + "_" + str(self.nb_connect)
        self.connections.append(
            Connection(name, self.hubs[zone1], self.hubs[zone2], capacity))
        self.nb_connect += 1

    def check_connect_options(self, matches: list[str]) -> int:
        if len(matches) > 1:
            raise ParsingError(self.i, "only one option available for a connection")
        options = matches[0][1:-1].strip().split("=")
        if options[0] != ConnectionOptions.CAP.value:
            raise ParsingError(self.i, "only option 'max_link_capacity' available for a connection")
        try:
            int_value = int(options[1])
            if int_value <= 0:
                raise ParsingError(self.i, "a connection must have at least 1 of capacity")
        except Exception:
            raise ParsingError(self.i, "a connection must have at least 1 of capacity")
        return int_value

    def map_builder(self) -> Map:
        """Build the map"""
        start = next(z for z in self.hubs.values() if isinstance(z, StartZone))
        end = next(z for z in self.hubs.values() if isinstance(z, EndZone))
        return Map(start, end, self.hubs, self.connections, self.drones)

    def connections_builder(self) -> None:
        """Build the bidirectional adjacency list of each zone from the connections"""
        for c in self.connections :
            c.zone1.hubs_connected.add(c.zone2)
            c.zone2.hubs_connected.add(c.zone1)
