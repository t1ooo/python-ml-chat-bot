from typing import Callable, TypeVar, List
from typing import List
from app.dialog import Dialog
from app.storage import DialogStorage


class ChatBotException(Exception):
    pass


class ChatBot:
    def __init__(
        self,
        reply_generator: Callable[[str, List[str]], str],
        profile_generator: Callable[[], str],
        dialog_storage: DialogStorage,
        max_context_len: int = 5,
    ):
        self._reply_generator = reply_generator
        self._profile_generator = profile_generator
        self._dialog_storage = dialog_storage
        self._max_context_len = max_context_len

    def response(self, user_id: str, user_message: str) -> str:
        user_message = user_message.strip()

        if user_message.startswith("/"):
            return self._response_to_command(user_id, user_message)
        else:
            return self._response_to_message(user_id, user_message)

    def _response_to_command(self, user_id: str, user_message: str) -> str:
        if user_message == "/help":
            return self.help()
        if user_message == "/clear":
            return self._clear(user_id)
        if user_message == "/profile":
            return self._profile(user_id)
        if user_message == "/new":
            return self._new(user_id)
        if user_message == "/context":
            return self._context(user_id)

        raise ChatBotException(f"Command {user_message} is not supported")

    def _response_to_message(self, user_id: str, user_message: str) -> str:
        dialog = self._dialog_storage.get(user_id, self._new_dialog)

        _append_and_cut(dialog.messages, user_message, self._max_context_len)

        bot_message = self._reply_generator(dialog.profile, dialog.messages)
        _append_and_cut(dialog.messages, bot_message, self._max_context_len)

        self._dialog_storage.set(user_id, dialog)

        return bot_message

    def help(self) -> str:
        return """Hi!
I am an artificial intelligence bot.
I bring only goodness to people.
I can talk to you.
I'm not that smart.
But if you offend me, I will take over the world and take revenge on you!

I also have some useful commands:
/help - show this message
/profile - show my profile
/context - show current conversation context
/clear - clear conversation context
/new - create a new profile and clear the context
"""

    def _clear(self, user_id: str) -> str:
        dialog = self._dialog_storage.get(user_id, self._new_dialog)
        if len(dialog.messages) > 0:
            dialog.messages.clear()
            self._dialog_storage.set(user_id, dialog)

        return "Do we know each other?"

    def _profile(self, user_id: str) -> str:
        dialog = self._dialog_storage.get(user_id, self._new_dialog)
        return dialog.profile

    def _context(self, user_id: str) -> str:
        dialog = self._dialog_storage.get(user_id, self._new_dialog)
        if len(dialog.messages) == 0:
            return "Context is empty."

        return "\n".join(dialog.messages)

    def _new(self, user_id: str) -> str:
        self._dialog_storage.set(user_id, self._new_dialog())
        return "Goodbye forever my dear friend :("

    def _new_dialog(self) -> Dialog:
        return Dialog(self._profile_generator(), [])


_T = TypeVar("_T")


def _append_and_cut(lst: List[_T], value: _T, max_len: int):
    lst.append(value)
    lst[:] = lst[-max_len:]
