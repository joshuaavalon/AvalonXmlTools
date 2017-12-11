import json
from datetime import datetime
from os import listdir, rename, makedirs
from os.path import isfile, join
from typing import Optional, Any, Dict

from youtube_dl import YoutubeDL

from tool import convert_size, valid_dir
from tool.argument import Argument, ask_inputs, add_arguments
from tool.plex import Episode, XmlSerializer

_arguments = [
    Argument("yid", type=str, meta="<youtube playlist id>"),
    Argument("prefix", abbr="p", type=str, default=None, meta="<prefix>", help="Output file name prefix"),
    Argument("output", abbr="o", type=valid_dir, default="output", meta="<output directory>",
             help="Output directory of the xml(s) (default: current)"),
    Argument("season", abbr="s", type=int, default=1, meta="<season number>",
             help="Season number of the xml(s) (default: %(default)s)"),
    Argument("mpaa", abbr="m", type=str, default=None, allow_default_none=True, meta="<mpaa>",
             help="Common mpaa of all the generate xml(s)")
]


def create_subparser(subparsers):
    command = "youtube"
    parser = subparsers.add_parser(command, help="Generate xml file(s).")
    add_arguments(parser, _arguments)
    return command, _download_youtube_playlist


# noinspection PyMethodMayBeStatic
class _Logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)


def _hook(d):
    if d["status"] == "downloading":
        file_name = d["filename"]
        message = f"Downloading: {file_name}"
        if "eta" in d:
            second = d["eta"]
            m, s = divmod(second, 60)
            h, m = divmod(m, 60)
            message += f" ETA: {'%d:%02d:%02d' % (h, m, s)}"
        if "speed" in d:
            message += f" {convert_size(d['speed'])}/s"
        print(message)


_default_opts = {
    "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio",
    "merge_output_format": "mp4",
    "logger": _Logger(),
    "progress_hooks": [_hook],
    "outtmpl": "%(id)s.%(ext)s",
    "writeinfojson": True,
    "writethumbnail": True
}


def _download_youtube(url: str, opts: Optional[Dict[str, Any]] = None):
    if opts is None:
        opts = _default_opts
    else:
        opts = {**_default_opts, **opts}
    with YoutubeDL(opts) as ydl:
        ydl.download([url])


def _download_youtube_playlist(args):
    if args is None:
        args = ask_inputs(_arguments)
    try:
        makedirs(args.output)
    except OSError:
        pass
    url = f"https://www.youtube.com/playlist?list={args.yid}"
    _download_youtube(url)
    for file in listdir("."):
        if isfile(file) and file.endswith(".info.json"):
            with open(file, "r", encoding="utf-8") as json_file:
                info = json.loads(json_file.read())
            if info is not None:
                vid = info["id"]
                episode_index = info["playlist_index"]
                aired = datetime.strptime(info["upload_date"], "%Y%m%d")
                file_name = f"{args.prefix} - s{str(args.season).zfill(2)}e{str(episode_index).zfill(2)}"
                episode = Episode(name=args.prefix,
                                  season=args.season,
                                  episode=episode_index,
                                  title=info["title"],
                                  aired=aired,
                                  mpaa=args.mpaa,
                                  plot=info["description"])
                XmlSerializer().serialize(episode, output=args.output)
                exts = [".mp4", ".jpg", ".info.json"]
                for ext in exts:
                    try:
                        old_name = f"{vid}{ext}"
                        new_name = f"{file_name}{ext}"
                        rename(old_name, join(args.output, new_name))
                    except OSError as e:
                        print(e)
