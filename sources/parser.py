class Parser():
    def __init__(self, file: str) -> None:
        self.start = 0
        self.end = 0
        try:
            text = open(file)
            self.text = text.read()
        except FileNotFoundError as e:
            print(e)

    def check_file(self) -> bool:
        if not self.text:
            return False
        all_rows = self.text.splitlines()
        rows: list[str] = []
        for row in all_rows:
            line = row.strip()
            if not line == "" and line:



                for letter in line:
                    if not letter.isspace() and letter == "#":
                        rows.remove(line)
                        break
                    if letter == "#":
                        index = line.index("#")
                        line = line[:index]

        print(rows)
        return True


if __name__ == "__main__":

    parser = Parser("test.txt")
    parser.check_file()