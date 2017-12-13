import shlex
from argparse import ArgumentParser
from types import SimpleNamespace
from typing import Optional, Callable, TypeVar, Generic, Any, Union, List

T = TypeVar("T")


# noinspection PyShadowingBuiltins
class Argument(Generic[T]):
    def __init__(self, name: str, type: Callable[[str], T], abbr: Optional[str] = None,
                 default: Optional[Union[T, List[T]]] = None, meta: Optional[str] = None, help: Optional[str] = None,
                 allow_default_none: bool = False, nargs: Optional[str] = None):
        if " " in name:
            raise ValueError("Name cannot contain space.")
        self.name = name  # type: str
        self._type = type  # type: Callable[[str], T]
        self._abbr = abbr  # type: Optional[str]
        self._default = default  # type: Optional[T]
        self._meta = meta  # type: Optional[str]
        self._help = help  # type: Optional[str]
        self._allow_default_none = allow_default_none  # type: bool
        if nargs is None and isinstance(default, list):
            nargs = "+"
        self._nargs = nargs  # type: Optional[str]

    def add_argument(self, parser: ArgumentParser):
        if self._abbr is None:
            self._add_positional_argument(parser)
        else:
            self._add_optional_argument(parser)

    def _add_positional_argument(self, parser: ArgumentParser):
        kwargs = self._create_arguments()
        parser.add_argument(self.name, **kwargs)

    def _add_optional_argument(self, parser: ArgumentParser):
        kwargs = self._create_arguments()
        parser.add_argument(f"-{self._abbr}", f"--{self.name}", **kwargs)

    def _create_arguments(self) -> dict:
        kwargs = {}
        if self._type != bool:
            self._add_to_dict(kwargs, "type", self._type)
            self._add_to_dict(kwargs, "default", self._default)
            self._add_to_dict(kwargs, "metavar", self._meta)
            self._add_to_dict(kwargs, "help", self._help)
            self._add_to_dict(kwargs, "nargs", self._nargs)
        else:
            self._add_to_dict(kwargs, "action", 'store_false' if self._default else 'store_true')
        return kwargs

    def _add_to_dict(self, dict: dict, key: str, value: Optional[Any]):
        if value is None and (not self._allow_default_none or key != "default"):
            return
        dict[key] = value

    def ask_input(self) -> Optional[Union[T, List[T]]]:
        has_default = self._default is not None or self._allow_default_none
        default_value = self._default
        if isinstance(self._default, str):
            default_value = f"\"{default_value}\""
        default_str = f"(default: {default_value})" if has_default else ""
        while True:
            try:
                user_input = input(f"Enter {self._meta}{default_str}: ")
                if not user_input and has_default:
                    return self._default
                if self._nargs is not None:
                    return [self._type(i) for i in shlex.split(user_input)]
                else:
                    return self._type(user_input)
            except ValueError:
                print("Invalid input!")


def ask_inputs(args: List[Argument]):
    result = SimpleNamespace()
    for arg in args:
        setattr(result, arg.name, arg.ask_input())
    return result


def add_arguments(parser: ArgumentParser, args: List[Argument]):
    for arg in args:
        arg.add_argument(parser)
