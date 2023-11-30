from rich.console import Console
import argparse
import traceback

console = Console()

parser = argparse.ArgumentParser()
parser.add_argument("-l", "--log", type=str, default="none")
args = parser.parse_args()

debug_mode = {
    "all": True if args.log == "all" else False,
    "time": True if args.log == "all" or args.log == "time" else False,
    "action": True if args.log == "all" or args.log == "action" else False,
    "episode": True if args.log == "all" or args.log == "episode" else False,
    "damage": True if args.log == "all" or args.log == "damage" else False
}

pickle_file = None

def log(*strings):
    frame = traceback.extract_stack()[-2]
    line_number = frame.lineno
    function_name = frame.name
    message = " ".join([str(string) for string in strings])
    console.print(f"[bold pink1]{function_name}[/bold pink1] (line {line_number}): [bold]{message}[/bold]")