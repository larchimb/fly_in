import sys
from srcs.parser import Parser
from srcs.models import ParsingError
from srcs.map import Map, MapDisplay

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