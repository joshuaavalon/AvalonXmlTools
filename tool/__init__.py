from argparse import ArgumentTypeError
from datetime import datetime
from fnmatch import fnmatch
from os import walk, listdir
from os.path import isdir, join, isfile, getmtime
from typing import Dict
from xml import etree
# noinspection PyProtectedMember
from xml.etree.ElementTree import Element, Comment, ProcessingInstruction, _escape_cdata, \
    _escape_attrib, QName


def valid_date(date_str: str) -> datetime:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0}".format(date_str)
        raise ArgumentTypeError(msg)


def valid_dir(path_str: str) -> str:
    if path_str == "" or isdir(path_str):
        return path_str
    raise TypeError("{0} is not a directory".format(path_str))


def valid_file(path_str: str) -> str:
    if isfile(path_str):
        return path_str
    raise TypeError("{0} is not a file".format(path_str))


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


def replace_words(source: str, replacement: Dict[str, str]) -> str:
    result = source
    for word in replacement.keys():
        result = result.replace(word, replacement[word])
    return result


def invert_dict(source: dict) -> dict:
    return {v: k for k, v in source.items()}


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
