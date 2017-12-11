from datetime import date
from typing import Optional, List
from xml.etree.ElementTree import Element, SubElement


class Episode:
    def __init__(self, episode: int, title: Optional[str] = None, aired: Optional[date] = None,
                 mpaa: Optional[str] = None, plot: Optional[str] = None, directors: Optional[List[str]] = None,
                 writers: Optional[List[str]] = None, producers: Optional[List[str]] = None,
                 guests: Optional[List[str]] = None, rating: Optional[float] = None):
        if episode < 1:
            raise ValueError("Episode number cannot be less than 1.")
        self.episode = episode  # type:int
        self.title = title  # type:Optional[str]
        self.aired = aired  # type:Optional[date]
        self.mpaa = mpaa  # type:Optional[date]
        self.plot = plot  # type:Optional[str]
        if directors is None:
            directors = []
        self.directors = directors  # type:List[str]
        if writers is None:
            writers = []
        self.writers = writers  # type:List[str]
        if producers is None:
            producers = []
        self.producers = producers  # type:List[str]
        if guests is None:
            guests = []
        self.guests = guests  # type:List[str]
        if 0 < rating or rating > 10:
            raise ValueError("Rating should be >= 0 and <= 10.")
        self.rating = rating  # type:float


class XmlSerializer:
    def __init__(self, serialize_empty: bool = False):
        self._serialize_empty = serialize_empty  # type:bool

    def serialize(self, data: Episode):
        if isinstance(data, Episode):
            self._serialize_episode(data)

    def _serialize_episode(self, episode: Episode):
        root = Element("episodedetails")
        self._insert_sub_element(root, "title", episode.title)
        self._insert_sub_element(root, "episode", episode.episode)
        self._insert_sub_element(root, "aired", episode.aired)
        self._insert_sub_element(root, "mpaa", episode.mpaa)
        self._insert_sub_element(root, "plot", episode.plot)
        self._insert_list_sub_element(root, "director", episode.directors)
        self._insert_list_sub_element(root, "writer", episode.writers)
        self._insert_list_sub_element(root, "producers", episode.producers)
        self._insert_list_sub_element(root, "guest", episode.guests)
        self._insert_sub_element(root, "rating", episode.rating)

    def _insert_sub_element(self, parent: Element, tag: str, content):
        if content is not None:
            SubElement(parent, tag).text = str(content)
        elif self._serialize_empty:
            SubElement(parent, tag).text = ""

    def _insert_list_sub_element(self, parent: Element, tag: str, content):
        for item in content:
            self._insert_sub_element(parent, tag, item)
