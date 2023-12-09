from typing import List
import unittest

from app.bot import ChatBot, ChatBotException
from app.storage import LRUDialogStorage


class ChatBotTests(unittest.TestCase):
    _MAX_CONTEXT_LEN = 3

    def _chat_bot(self):
        def reply_generator(profile: str, messages: List[str]) -> str:
            return f"reply:{messages[-1]}"

        i = -1

        def profile_generator() -> str:
            nonlocal i
            i += 1
            return f"some_profile {i}"

        dialog_storage = LRUDialogStorage(10)
        return ChatBot(
            reply_generator=reply_generator,
            profile_generator=profile_generator,
            dialog_storage=dialog_storage,
            max_context_len=self._MAX_CONTEXT_LEN,
        )

    def test_bad_command(self):
        bot = self._chat_bot()

        self.assertRaisesRegex(
            ChatBotException,
            "Command /badcommand is not supported",
            bot.response,
            "id",
            "/badcommand",
        )
        self.assertRaisesRegex(
            ChatBotException, "Command / is not supported", bot.response, "id", "/"
        )

    def test_help_command(self):
        bot = self._chat_bot()

        r = bot.response("id", "/help")
        self.assertTrue(len(r) > 0)
        # should return same help message
        self.assertEqual(r, bot.response("other_id", "/help"))

    def test_profile_command(self):
        bot = self._chat_bot()

        profile = bot.response("id", "/profile")
        other_profile = bot.response("other_id", "/profile")

        # should return same profile for same id
        self.assertEqual(profile, bot.response("id", "/profile"))

        # should return different profiles for different ids
        self.assertNotEqual(profile, other_profile)

    def test_context_command(self):
        bot = self._chat_bot()

        self.assertEqual(bot.response("id", "/context"), "Context is empty.")

        bot.response("id", "message_1")
        bot.response("id", "message_2")

        bot.response("other_id", "message_4")

        # should return last self._MAX_CONTEXT_LEN messages
        self.assertEqual(
            bot.response("id", "/context"),
            "reply:message_1\nmessage_2\nreply:message_2",
        )

        # should return different context for different ids
        self.assertEqual(
            bot.response("other_id", "/context"), "message_4\nreply:message_4"
        )

    def test_clear_command(self):
        bot = self._chat_bot()

        profile = bot.response("id", "/profile")

        bot.response("id", "message_1")
        bot.response("id", "message_2")
        bot.response("id", "message_3")

        bot.response("other_id", "message_1")
        bot.response("other_id", "message_2")
        bot.response("other_id", "message_3")

        self.assertEqual(bot.response("id", "/clear"), "Do we know each other?")
        # should return empty context
        self.assertEqual(bot.response("id", "/context"), "Context is empty.")
        # should return same profile info
        self.assertEqual(profile, bot.response("id", "/profile"))

        # should't clear context for other_id
        self.assertNotEqual(bot.response("other_id", "/context"), "Context is empty.")

    def test_new_command(self):
        bot = self._chat_bot()

        profile = bot.response("id", "/profile")
        other_profile = bot.response("other_id", "/profile")

        bot.response("id", "message_1")
        bot.response("id", "message_2")
        bot.response("id", "message_3")

        bot.response("other_id", "message_1")
        bot.response("other_id", "message_2")
        bot.response("other_id", "message_3")

        self.assertEqual(
            bot.response("id", "/new"), "Goodbye forever my dear friend :("
        )
        # should return empty context
        self.assertEqual(bot.response("id", "/context"), "Context is empty.")
        # should return new profile info
        self.assertNotEqual(profile, bot.response("id", "/profile"))

        # should't clear context for other_id
        self.assertNotEqual(bot.response("other_id", "/context"), "Context is empty.")
        # should't generate new profile for other_id
        self.assertEqual(other_profile, bot.response("other_id", "/profile"))

    def test_new_message(self):
        bot = self._chat_bot()

        self.assertEqual(bot.response("id", "message_1"), "reply:message_1")
        self.assertEqual(bot.response("other_id", "message_1"), "reply:message_1")


if __name__ == "__main__":
    unittest.main()
