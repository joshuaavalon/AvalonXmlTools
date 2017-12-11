import json
import re
from os.path import basename, splitext

from tool import valid_dir, find_files
from tool.argument import Argument, add_arguments, ask_inputs

_arguments = [
    Argument("input", abbr="i", type=valid_dir, default=".", meta="<Input folder>",
             help="Source folder (default: current)"),
    Argument("output", abbr="o", type=str, default="cast.json", meta="<Output folder>",
             help="Output file (default: %(default)s)"),
    Argument("prefix", abbr="p", type=str, default="", meta="<prefix>",
             help="Prefix of generated url(s) (default: None)")
]


def create_subparser(subparsers):
    command = "cast"
    parser = subparsers.add_parser(command, help="Create cast.json.")
    add_arguments(parser, _arguments)
    return command, _cast


def _cast(args):
    if args is None:
        args = ask_inputs(_arguments)
    casts = {}
    versions = {}
    for file in find_files(args.input, ["*.png", "*.jpg", "*.jpeg", "*.gif"], recursive=False):
        fullname = basename(file)
        name = splitext(fullname)[0]
        result = re.search("(.*)\.(\d*)", name, re.IGNORECASE)
        if result:
            name = result.group(1)
            version = int(result.group(2))
        else:
            version = 0
        if name not in casts or versions[name] < version:
            casts[name] = args.prefix + fullname
            versions[name] = version
    json_str = json.dumps(casts, indent=4, sort_keys=True, ensure_ascii=False)
    with open(args.output, encoding="utf-8", mode="w") as file:
        file.write(json_str)
