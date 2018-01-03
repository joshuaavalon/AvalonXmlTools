from datetime import datetime
from os.path import join
from typing import Optional, List
from xml.etree.ElementTree import Element, SubElement, ElementTree


class Episode:
    def __init__(self, name: str, season: int, episode: int, title: Optional[str] = None,
                 aired: Optional[datetime] = None, mpaa: Optional[str] = None, plot: Optional[str] = None,
                 directors: Optional[List[str]] = None, writers: Optional[List[str]] = None,
                 producers: Optional[List[str]] = None, guests: Optional[List[str]] = None,
                 rating: Optional[float] = None):
        if season < 0:
            raise ValueError("Season number cannot be less than 0.")
        if episode < 1:
            raise ValueError("Episode number cannot be less than 1.")
        self.name = name
        self.season = season  # type: int
        self.episode = episode  # type: int
        self.title = title  # type: Optional[str]
        self.aired = aired  # type: Optional[datetime]
        self.mpaa = mpaa  # type: Optional[datetime]
        self.plot = plot  # type: Optional[str]
        if directors is None:
            directors = []
        self.directors = directors  # type: List[str]
        if writers is None:
            writers = []
        self.writers = writers  # type: List[str]
        if producers is None:
            producers = []
        self.producers = producers  # type: List[str]
        if guests is None:
            guests = []
        self.guests = guests  # type: List[str]
        if rating is not None and (0 < rating or rating > 10):
            raise ValueError("Rating should be >= 0 and <= 10.")
        self.rating = rating  # type: Optional[float]


class XmlSerializer:
    def __init__(self, serialize_empty: bool = False):
        self._serialize_empty = serialize_empty  # type: bool

    def serialize(self, data: Episode, folder: str = "", encoding: str = "utf-8", output: Optional[str] = None,
                  short_empty_elements: bool = False):
        root = self._serialize_episode(data)  # type: Element
        tree = ElementTree(element=root)  # type: ElementTree
        if output is None:
            file_name = "{0} - s{1:02d}e{2:02d}.xml".format(data.name, data.season, data.episode)
            output = join(folder, file_name)
        tree.write(output, encoding=encoding, short_empty_elements=short_empty_elements)

    def _serialize_episode(self, episode: Episode) -> Element:
        root = Element("episodedetails")
        self._insert_sub_element(root, "title", episode.title)
        self._insert_sub_element(root, "episode", episode.episode)
        self._insert_sub_element(root, "aired", episode.aired.date() if episode.aired is not None else None)
        self._insert_sub_element(root, "mpaa", episode.mpaa)
        self._insert_sub_element(root, "plot", episode.plot)
        self._insert_list_sub_element(root, "director", episode.directors)
        self._insert_list_sub_element(root, "writer", episode.writers)
        self._insert_list_sub_element(root, "producers", episode.producers)
        self._insert_list_sub_element(root, "guest", episode.guests)
        self._insert_sub_element(root, "rating", episode.rating)
        return root

    def _insert_sub_element(self, parent: Element, tag: str, content):
        if content is not None:
            SubElement(parent, tag).text = str(content)
        elif self._serialize_empty:
            SubElement(parent, tag).text = ""

    def _insert_list_sub_element(self, parent: Element, tag: str, content):
        for item in content:
            self._insert_sub_element(parent, tag, item)
