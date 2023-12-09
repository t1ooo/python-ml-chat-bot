from typing import List


class Dialog:
    def __init__(self, profile: str, messages: List[str]):
        self.profile = profile
        self.messages = messages
