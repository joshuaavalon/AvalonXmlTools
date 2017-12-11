import json
# noinspection PyProtectedMember
from xml.etree.ElementTree import Element, SubElement, ElementTree

from tool import valid_file, find_files
from tool.argument import Argument, add_arguments, ask_inputs

_arguments = [
    Argument("cast", abbr="c", type=valid_file, default="cast.json", meta="<cast JSON>",
             help="Cast JSON used for update (default: cast.json)"),
    Argument("day", abbr="d", type=int, default=1, meta="<last modify>",
             help="Day difference of xml to be updated. (default: %(default)s)")
]


def create_subparser(subparsers):
    command = "thumb"
    parser = subparsers.add_parser(command, help="Update <thumb> in xml file(s).")
    add_arguments(parser, _arguments)
    return command, _thumb


def _thumb(args):
    if args is None:
        args = ask_inputs(_arguments)
    with open(args.cast, mode="r", encoding="utf-8") as casts_file:
        casts = json.load(casts_file)
    undefined = set()
    day_diff = args.day
    if day_diff < 0:
        day_diff = None
    for file in find_files(".", "*.xml", day_diff):
        with open(file, mode="r", encoding="utf-8") as xml:
            first_line = xml.readline()
            if "tvshow" not in first_line and "movie" not in first_line:
                continue
        tree = ElementTree(file=file)
        root = tree.getroot()  # type: Element
        if root.tag not in ["tvshow", "movie"]:
            continue
        for element in tree.iter():  # type: Element
            if element.text is not None and element.text.isspace():
                element.text = None
            element.tail = None
        for actor in tree.findall("actor"):  # type: Element
            name_element = actor.find("name")  # type: Element
            if name_element.text in casts:
                thumb_element = actor.find("thumb")  # type: Element
                if thumb_element is None:
                    thumb_element = SubElement(actor, "thumb")
                thumb_element.text = casts[name_element.text]
            else:
                undefined.add(name_element.text)

        tree.write(file, encoding="utf-8", short_empty_elements=False)
    for actor in undefined:
        print(actor)
