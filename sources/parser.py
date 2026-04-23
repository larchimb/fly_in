from enum import Enum

class KeyTypes(Enum):
    NBD = "nb_drones"
    STR = "start"
    END = "end"
    HUB = "hub"
    CON = "connection"

class Parser():
    def __init__(self) -> None:
        self.rows: list[str] = []
        self.hub_names = list[str]
        self.connection_names = list[str]

    def check_file(self, file: str) -> None:
        """Check all conditions for entry's file"""
        try:
            text: str = open(file).read()
        except (FileNotFoundError, Exception) as e:
            raise (e)
        self.delete_comments(text)
        if not self.rows:
            raise Exception(f"[ERROR] {file} is empty or contain comments only")
        self.check_drones()
        self.check_hubs()
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
        """Check if the number of drone is positive
        and at the beginning of the entry's file."""
        index: int = next((i for i, row in enumerate(self.rows) if row))
        key, _, value = self.rows[index].strip().partition(": ")

        if not key.strip() == "nb_drones":
            raise ValueError(f"[ERROR] line {index + 1}: \n"
                             "First line must be: 'nb_drones: {positive int}'\n"
                             f"You have: '{key.strip() + _ + value}'")
        try:
            value = int(value.strip())
            if value <= 0:
                raise ValueError
        except ValueError:
            raise ValueError(
                f"[ERROR] Line {index + 1} -> {key}: "
                "You must have a positive number of drone"
                )

    def check_hubs(self) -> None:
        """Check all hub's name, value and """
        key_names = [(index, value.strip().partition(": ")) for index, value in enumerate(self.rows)]
        print(key_names)


if __name__ == "__main__":
    try:
        parser = Parser()
        parser.check_file("test.txt")
    except Exception as e:
        print(e)