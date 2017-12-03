import json
from argparse import ArgumentParser, HelpFormatter, ArgumentTypeError
from datetime import datetime, timedelta
from fnmatch import fnmatch
from os import walk, listdir
from os.path import isdir, join, isfile, getmtime, splitext, basename
from xml import etree
# noinspection PyProtectedMember
from xml.etree.ElementTree import Element, SubElement, ElementTree, Comment, ProcessingInstruction, _escape_cdata, \
    _escape_attrib, QName
import re
from unicodedata import normalize

class _HelpFormatter(HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings or action.nargs == 0:
            return super()._format_action_invocation(action)
        default = self._get_default_metavar_for_optional(action)
        args_string = self._format_args(action, default)
        return ", ".join(action.option_strings) + " " + args_string


def find_files(directory, pattern, day_diff=None, recursive=True):
    now = datetime.now()
    if isinstance(pattern, str):
        pattern = [pattern]
    if recursive:
        for root, dirs, files in walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".")
                       and (
                           day_diff is None or (
                               now - datetime.fromtimestamp(getmtime(join(root, d)))).days <= day_diff)]
            for base_name in files:
                filename = join(root, base_name)
                if any_match(base_name, pattern) \
                        and (day_diff is None or (now - datetime.fromtimestamp(getmtime(filename))).days <= day_diff):
                    yield filename
    else:
        for file in listdir(directory):
            path = join(directory, file)
            if isfile(path) and any_match(file, pattern):
                yield path


def any_match(name, patterns):
    return any(fnmatch(name, pattern) for pattern in patterns)


def _create_parsers():
    parser = ArgumentParser(prog="Avalon Xml Tools", description="Version 1.0.2", formatter_class=_HelpFormatter)
    subparsers = parser.add_subparsers(dest="command")

    subparsers_factories = [_create_create_subparser,
                            _create_thumb_subparser,
                            _create_cast_subparser,
                            _create_normalize_subparser]
    funcs = {}
    for factory in subparsers_factories:
        command, func = factory(subparsers)
        funcs[command] = func

    return parser, funcs


def _valid_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0}".format(date_str)
        raise ArgumentTypeError(msg)


def _valid_dir(path_str):
    if path_str == "" or isdir(path_str):
        return path_str
    raise TypeError("{0} is not a directory".format(path_str))


def _valid_file(path_str):
    if isfile(path_str):
        return path_str
    raise TypeError("{0} is not a file".format(path_str))


# ============================ Create Start ============================

def create(args):
    if args.start_episode > args.end_episode:
        raise ValueError("Start episode number cannot be greater than end episode number")
    start_date = args.date  # type
    for index, episode_num in enumerate(range(args.start_episode, args.end_episode + 1)):
        aired = start_date + timedelta(days=args.increment * index) if start_date is not None else None  # type
        root = _generate_xml(index=index, episode_num=episode_num, aired=aired, args=args)  # type: Element
        file_name = "{0} - s{1:02d}e{2:02d}.xml".format(args.name, args.season, episode_num)  # type
        tree = ElementTree(element=root)  # type: ElementTree
        tree.write(join(args.output, file_name), encoding="utf-8", short_empty_elements=False)


def _create_create_subparser(subparsers):
    command = "create"
    parser = subparsers.add_parser(command, help="Generate xml file(s).")
    parser.add_argument("name", type=str)
    parser.add_argument("-o", "--output", type=_valid_dir, default="", metavar="<output directory>",
                        help="Output directory of the xml(s) (default: current)")
    parser.add_argument("-s", "--season", type=int, default=1, metavar="<season number>",
                        help="Season number of the xml(s) (default: %(default)s)")
    parser.add_argument("-D", "--date", type=_valid_date, default=None, metavar="<start date>",
                        help="Start date of the xml file(s) (default: %(default)s)")
    parser.add_argument("-m", "--mpaa", type=str, default="", metavar="<mpaa>",
                        help="Common mpaa of all the generate xml(s)")
    parser.add_argument("-d", "--directors", type=str, default=[], nargs="+", metavar="<director(s) name>",
                        help="Common director(s) of all the generate xml(s)")
    parser.add_argument("-w", "--writers", type=str, default=[], nargs="+", metavar="<writer(s) name>",
                        help="Common writer(s) of all the generate xml(s)")
    parser.add_argument("-p", "--producers", type=str, default=[], nargs="+", metavar="<producer(s) name>",
                        help="Common producer(s) of all the generate xml(s)")
    parser.add_argument("-g", "--guests", type=str, default=[], nargs="+", metavar="<guest(s) name>",
                        help="Common guest(s) of all the generate xml(s)")
    parser.add_argument("-i", "--increment", type=int, default=7, metavar="<number of day(s)>",
                        help="Number of day(s) between each episode (default: %(default)s)")
    parser.add_argument("-S", "--start_episode", type=int, default=1, metavar="<start episode>",
                        help="Episode number of the start (inclusive) (default: %(default)s)")
    parser.add_argument("-E", "--end_episode", type=int, default=12, metavar="<end episode>",
                        help="Episode number of the end (inclusive) (default: %(default)s)")
    parser.add_argument("-r", "--rating", type=str, default="", metavar="<rating>",
                        help="Common rating(s) of all the generate xml(s)")
    parser.add_argument("-t", "--title", type=str, default="", metavar="<title>",
                        help="Common title(s) of all the generate xml(s)")
    return command, create


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


# ============================  Create End  ============================

# ============================  Thumb Start ============================


def _create_thumb_subparser(subparsers):
    command = "thumb"
    parser = subparsers.add_parser(command, help="Update <thumb> in xml file(s).")
    parser.add_argument("-c", "--cast", type=_valid_file, default="cast.json", metavar="<cast JSON>",
                        help="Cast JSON used for update (default: cast.json)")
    parser.add_argument("-d", "--day", type=int, default=1, metavar="<last modify>",
                        help="Day difference of xml to be updated. (default: %(default)s)")

    return command, thumb


def thumb(args):
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


# ============================   Thumb End  ============================

# ============================  Cast Start  ============================

def _create_cast_subparser(subparsers):
    command = "cast"
    parser = subparsers.add_parser(command, help="Create cast.json.")
    parser.add_argument("-i", "--input", type=_valid_dir, default=".", metavar="<Input folder>",
                        help="Source folder (default: current)")
    parser.add_argument("-o", "--output", type=str, default="cast.json", metavar="<Output folder>",
                        help="Output file (default: %(default)s)")
    parser.add_argument("-p", "--prefix", type=str, default="", metavar="<prefix>",
                        help="Prefix of generated url(s) (default: None)")
    return command, cast


def cast(args):
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


# ============================   Cast End   ============================

# ==========================  Normalize Start ===========================


def _create_normalize_subparser(subparsers):
    command = "normalize"
    parser = subparsers.add_parser(command, help="Normalize string in xml file.")
    parser.add_argument("file", type=_valid_file)

    return command, normal


def normal(args):
    with open(args.file, mode="r+", encoding="utf-8") as file:
        content = normalize('NFKC', file.read())
        file.seek(0)
        file.write(content)
        file.truncate()



# ==========================   Normalize End  ==========================

def main():
    parser, funcs = _create_parsers()
    args = parser.parse_args()
    if args.command in funcs:
        funcs[args.command](args)
    else:
        parser.print_help()


# ============================  Hack Start  ============================

def _serialize_xml(write, elem, qnames, namespaces, short_empty_elements, addintend="    ", intend="", newl="\n",
                   **kwargs):
    tag = elem.tag
    text = elem.text
    if tag is Comment:
        write(intend + "<!--%s-->" % text)
    elif tag is ProcessingInstruction:
        write(intend + "<?%s?>" % text)
    else:
        tag = qnames[tag]
        if tag is None:
            if text:
                write(_escape_cdata(text))
            for e in elem:
                _serialize_xml(write, e, qnames, None, addintend=addintend, intend=addintend + intend, newl=newl,
                               short_empty_elements=short_empty_elements)
        else:
            write(intend + "<" + tag)
            items = list(elem.items())
            if items or namespaces:
                if namespaces:
                    for v, k in sorted(namespaces.items(),
                                       key=lambda x: x[1]):  # sort on prefix
                        if k:
                            k = ":" + k
                        write(" xmlns%s=\"%s\"" % (
                            k,
                            _escape_attrib(v)
                        ))
                for k, v in sorted(items):  # lexical order
                    if isinstance(k, QName):
                        k = k.text
                    if isinstance(v, QName):
                        v = qnames[v.text]
                    else:
                        v = _escape_attrib(v)
                    write(" %s=\"%s\"" % (qnames[k], v))
            if text or len(elem) or not short_empty_elements:
                write(">")
                if text is not None:
                    write(_escape_cdata(text))
                else:
                    if len(elem.getchildren()) > 0:
                        write(newl)
                for e in elem:
                    _serialize_xml(write, e, qnames, None, addintend=addintend, intend=addintend + intend, newl=newl,
                                   short_empty_elements=short_empty_elements)
                if len(elem.getchildren()) > 0:
                    write(intend)
                write("</" + tag + ">" + newl)
            else:
                write(" />" + newl)
    if elem.tail:
        write(_escape_cdata(elem.tail))


etree.ElementTree._serialize_xml = _serialize_xml
# noinspection PyProtectedMember
etree.ElementTree._serialize["xml"] = _serialize_xml

# ============================   Hack End   ============================

if __name__ == "__main__":
    main()
