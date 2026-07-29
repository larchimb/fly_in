from models import (
    MapError,
    Zone,
    StartZone,
    EndZone,
    RestrictedZone,
    PriorityZone,
    Connection,
    Drone,
)


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
        self.end.drone_in = 0
        self.start.drone_in = len(self.drones)

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
