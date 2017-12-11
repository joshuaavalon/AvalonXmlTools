from typing import Callable, Optional, List, Set, Dict


class MenuItem:
    def __init__(self, name: str, action: Optional[Callable[[], None]] = None, index: Optional[int] = None):
        self.name = name  # type: str
        self.action = action  # type: Optional[Callable[[], None]]
        self.index = index  # type: Optional[int]


class Menu:
    def __init__(self, items: List[MenuItem], start_index: int = 1):
        if len(items) <= 0:
            raise ValueError(f"Items cannot be empty.")
        used_index = set()  # type: Set[int]
        current_index = start_index  # type: int
        self._items = {}  # type: Dict[int,MenuItem]
        for item in items:
            index = item.index
            if index is not None:
                if index in used_index:
                    raise ValueError(f"{index} is already used.")
            else:
                while current_index in used_index:
                    current_index += 1
                index = current_index
                current_index += 1
            used_index.add(index)
            self._items[index] = item

    def show(self) -> int:
        items = self._items
        keys = list(items.keys())  # type: List[int]
        keys.sort()
        user_input = None  # type: Optional[int]
        error = False  # type: bool
        while user_input is None:
            print()
            if error:
                print("Invalid action!")
            for key in keys:
                print(f"{key}. {items[key].name}")
            print()
            try:
                user_input = int(input("Please choose your action:"))
                if user_input not in items:
                    raise ValueError("Invalid key")
            except ValueError:
                error = True
                user_input = None
        action = items[user_input].action
        if action is not None:
            action()
        return user_input
