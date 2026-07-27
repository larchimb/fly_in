import sys
from parser import Parser
from models import ParsingError
from display import MapDisplay


def main() -> None:
    """The main programme"""
    if len(sys.argv) != 2:
        raise Exception("[ERROR]: No argument provide")
    parser = Parser()
    parser.check_file(sys.argv[1])
    map = parser.map_builder()
    MapDisplay(map)


if __name__ == "__main__":
    try:
        main()
    except (ParsingError, Exception) as e:
        print(e)
