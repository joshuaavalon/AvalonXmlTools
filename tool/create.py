from datetime import datetime
from datetime import timedelta
from os.path import join
# noinspection PyProtectedMember
from xml.etree.ElementTree import Element, SubElement, ElementTree

from tool import valid_dir, valid_date
from tool.argument import Argument, ask_inputs, add_arguments

"""
_arg_name = Argument("name", type=str)
_arg_output = Argument("output", abbr="o", type=valid_dir, default="", meta="<output directory>",
                       help="Output directory of the xml(s) (default: current)")

_arg_season = Argument("season", abbr="s", type=int, default=1, meta="<season number>",
                       help="Season number of the xml(s) (default: %(default)s)")
_arg_date = Argument("date", abbr="D", type=valid_date, default=None, meta="<start date>",
                     help="Start date of the xml file(s) (default: %(default)s)")
_arg_mpaa = Argument("mpaa", abbr="m", type=str, default="", meta="<mpaa>",
                     help="Common mpaa of all the generate xml(s)")
_arg_directors = Argument("directors", abbr="d", type=str, default=[], nargs="+", meta="<director(s) name>",
                          help="Common director(s) of all the generate xml(s)")
_arg_writers = Argument("writers", abbr="w", type=str, default=[], nargs="+", meta="<writer(s) name>",
                        help="Common writer(s) of all the generate xml(s)")
_arg_producers = Argument("producers", abbr="p", type=str, default=[], nargs="+", meta="<producer(s) name>",
                          help="Common producer(s) of all the generate xml(s)")
_arg_guests = Argument("guests", abbr="g", type=str, default=[], nargs="+", meta="<guest(s) name>",
                       help="Common guest(s) of all the generate xml(s)")
_arg_increment = Argument("increment", abbr="i", type=int, default=7, meta="<number of day(s)>",
                          help="Number of day(s) between each episode (default: %(default)s)")
_arg_start_episode = Argument("start_episode", abbr="S", type=int, default=1, meta="<start episode>",
                              help="Episode number of the start (inclusive) (default: %(default)s)")
_arg_end_episode = Argument("end_episode", abbr="E", type=int, default=12, meta="<end episode>",
                            help="Episode number of the end (inclusive) (default: %(default)s)")
_arg_rating = Argument("rating", abbr="r", type=str, default="", meta="<rating>",
                       help="Common rating(s) of all the generate xml(s)")
_arg_title = Argument("title", abbr="t", type=str, default="", meta="<title>",
                      help="Common title(s) of all the generate xml(s)")
                      """
_arguments = [
    Argument("name", type=str),
    Argument("output", abbr="o", type=valid_dir, default="", meta="<output directory>",
             help="Output directory of the xml(s) (default: current)"),
    Argument("season", abbr="s", type=int, default=1, meta="<season number>",
             help="Season number of the xml(s) (default: %(default)s)"),
    Argument("date", abbr="D", type=valid_date, default=None, meta="<start date>",
             help="Start date of the xml file(s) (default: %(default)s)"),
    Argument("mpaa", abbr="m", type=str, default="", meta="<mpaa>", help="Common mpaa of all the generate xml(s)"),
    Argument("directors", abbr="d", type=str, default=[], nargs="+", meta="<director(s) name>",
             help="Common director(s) of all the generate xml(s)"),
    Argument("writers", abbr="w", type=str, default=[], nargs="+", meta="<writer(s) name>",
             help="Common writer(s) of all the generate xml(s)"),
    Argument("producers", abbr="p", type=str, default=[], nargs="+", meta="<producer(s) name>",
             help="Common producer(s) of all the generate xml(s)"),
    Argument("guests", abbr="g", type=str, default=[], nargs="+", meta="<guest(s) name>",
             help="Common guest(s) of all the generate xml(s)"),
    Argument("increment", abbr="i", type=int, default=7, meta="<number of day(s)>",
             help="Number of day(s) between each episode (default: %(default)s)"),
    Argument("start_episode", abbr="S", type=int, default=1, meta="<start episode>",
             help="Episode number of the start (inclusive) (default: %(default)s)"),
    Argument("end_episode", abbr="E", type=int, default=12, meta="<end episode>",
             help="Episode number of the end (inclusive) (default: %(default)s)"),
    Argument("rating", abbr="r", type=str, default="", meta="<rating>",
             help="Common rating(s) of all the generate xml(s)"),
    Argument("title", abbr="t", type=str, default="", meta="<title>", help="Common title(s) of all the generate xml(s)")
]


def create_subparser(subparsers):
    command = "create"
    parser = subparsers.add_parser(command, help="Generate xml file(s).")
    add_arguments(parser, _arguments)
    return command, _create


def _create(args):
    if args is None:
        args = ask_inputs(_arguments)
    if args.start_episode > args.end_episode:
        raise ValueError("Start episode number cannot be greater than end episode number")
    start_date = args.date  # type
    for index, episode_num in enumerate(range(args.start_episode, args.end_episode + 1)):
        aired = start_date + \
                timedelta(days=args.increment * index) if start_date is not None else None  # type: datetime
        root = _generate_xml(index=index, episode_num=episode_num, aired=aired, args=args)  # type: Element
        file_name = "{0} - s{1:02d}e{2:02d}.xml".format(args.name, args.season, episode_num)  # type
        tree = ElementTree(element=root)  # type: ElementTree
        tree.write(join(args.output, file_name), encoding="utf-8", short_empty_elements=False)


def _generate_xml(index, episode_num, aired, args):
    root = Element("episodedetails")
    SubElement(root, "title").text = _parse_template_str(template=args.title, index=index, episode_num=episode_num,
                                                         aired=aired, args=args)
    SubElement(root, "episode").text = str(episode_num)
    SubElement(root, "aired").text = aired.strftime("%Y-%m-%d") if aired is not None else ""
    SubElement(root, "mpaa").text = args.mpaa
    SubElement(root, "plot").text = ""
    _set_list_tag(root, "director", args.directors)
    _set_list_tag(root, "writer", args.writers)
    _set_list_tag(root, "producer", args.producers)
    _set_list_tag(root, "guest", args.guests)
    SubElement(root, "rating").text = args.rating
    return root


def _set_list_tag(element, tag, values):
    for value in values:
        SubElement(element, tag).text = value


def _parse_template_str(template, index, episode_num, aired, args):
    result = template  # type
    result = result.replace("%I", str(index + 1))
    result = result.replace("%E", str(episode_num))
    if aired is not None:
        result = result.replace("%D", aired.strftime("%Y-%m-%d"))
    return result
