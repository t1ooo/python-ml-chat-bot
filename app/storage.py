from copy import deepcopy
from typing import Callable, Protocol
from cachetools import LRUCache
from app.dialog import Dialog


class DialogStorage(Protocol):
    def get(self, id: str, default: Callable[[], Dialog]) -> Dialog:
        ...

    def set(self, id: str, dialog: Dialog):
        ...


class LRUDialogStorage(DialogStorage):
    def __init__(self, maxsize: int):
        self.data: LRUCache[str, Dialog] = LRUCache(maxsize=maxsize)

    def get(self, id: str, default: Callable[[], Dialog]) -> Dialog:
        if id in self.data:
            return deepcopy(self.data[id])

        dialog = default()
        self.set(id, dialog)
        return dialog

    def set(self, id: str, dialog: Dialog):
        self.data[id] = deepcopy(dialog)
