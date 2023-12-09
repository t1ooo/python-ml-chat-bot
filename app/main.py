from dataclasses import dataclass
import secrets
import logging
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.bot import ChatBot, ChatBotException
from app.model import Godel
from app.profile import get_static_profile
from app.storage import LRUDialogStorage


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__file__)


class Message(BaseModel):
    text: str


@dataclass
class ResponseMessage:
    text: str


stor = LRUDialogStorage(maxsize=100)
app = FastAPI()
reply_generator = Godel()
bot = ChatBot(
    reply_generator=reply_generator,
    profile_generator=get_static_profile,
    dialog_storage=stor,
)


@app.exception_handler(ChatBotException)
async def exception_handler(e: ChatBotException):
    return JSONResponse(
        content={"error": str(e)},
    )


@app.get("/startchat")
async def start_chat() -> ResponseMessage:
    return ResponseMessage(bot.help())


@app.post("/chat")
async def chat(request: Request, response: Response, item: Message) -> ResponseMessage:
    user_id = request.cookies.get("user_id", "")
    logger.debug(f"user_id: {user_id}")
    if user_id == "":
        user_id = secrets.token_hex(32)
        response.set_cookie(key="user_id", value=user_id, secure=True)
        logger.debug(f"set user_id: {user_id}")

    message = bot.response(user_id, item.text)
    return ResponseMessage(message)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
