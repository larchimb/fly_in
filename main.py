import sys
from parser import Parser
from models import ParsingError
from display import Map, MapDisplay

def main() -> None:

    if len(sys.argv) != 2:
        raise Exception
    parser = Parser()
    parser.check_file(sys.argv[1])
    map = parser.map_builder()
    display = MapDisplay(map)


if __name__ == "__main__":
    try:
        main()
    except (ParsingError, Exception) as e:
        print(e)
