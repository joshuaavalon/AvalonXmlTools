from unicodedata import normalize

from tool import valid_file, replace_words, invert_dict
from tool.argument import Argument

_argument = Argument("file", type=valid_file, meta="<file>")


def create_subparser(subparsers):
    command = "normalize"
    parser = subparsers.add_parser(command, help="Normalize string in xml file.")
    _argument.add_argument(parser)
    return command, _normal


def _normal(args):
    if args is None:
        file_path = _argument.ask_input()
    else:
        file_path = args.file
    with open(file_path, mode="r+", encoding="utf-8") as file:
        content = normal(file.read())
        file.seek(0)
        file.write(content)
        file.truncate()


def normal(source: str) -> str:
    content = replace_words(source, _before)
    content = normalize("NFKC", content)
    return replace_words(content, _after)


_before = {
    "～": "$wave%",
    "&amp;": "$and%"
}

_after = {
    **invert_dict(_before),
    "...": "…",
    "．．．": "…"
}
