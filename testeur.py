import glob
from srcs.parser import Parser
from srcs.models import ParsingError

for path in sorted(glob.glob("maps/**/*.txt", recursive=True)):
    parser = Parser()
    try:
        parser.check_file(path)
        m = parser.map_builder()
        print(f"OK   {path} (turns={m.turn})")

    except (ParsingError, Exception) as e:
        print(f"FAIL {path}: {e}")