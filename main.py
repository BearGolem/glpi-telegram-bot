"""
Main exec file for telegram bot.
"""

import logging
import threading
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext

# from aiogram.dispatcher.filters import state
from aiogram.utils import executor
from aiogram.utils.exceptions import NetworkError

from bot.app import checker
from bot.app.core import dp
from bot.app.generic import generic, onboarding
from bot.app.bot_state import Form
import config


# TODO add /cancel


@dp.message_handler(commands=["start"], state="*")
async def start_message(message: types.Message, state: FSMContext) -> None:
    """Reacts on /start command in every state"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info("User ID %d issued /start command. State: %s", user_id, current_state)

    await generic.start_message(user_id, state)


@dp.message_handler(commands=["/help"], state="*")
async def help_message(message: types.Message, state: FSMContext) -> None:
    """Reacts on /help command in every state"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info("User ID %d issued /help command. State: %s", user_id, current_state)

    await generic.help_command(user_id)


@dp.message_handler(commands=["logout"], state="*")
async def logout_message(message: types.Message, state: FSMContext) -> None:
    """Reacts on /logout command in every state"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info("User ID %d issued /logout command. State: %s", user_id, current_state)

    await generic.logout(user_id=user_id, state=state)


# ONBOARDING
# =======================================================


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.to_enter_login)
async def process_to_enter_login(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_enter_login"""
    user_id: int = message.from_user.id
    text: str = message.text
    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d provided login: '%s'. State: %s", user_id, text, current_state
    )

    if message.is_command():
        await onboarding.process_cancel(
            user_id,
            state,
            "Что-то пошло не так? Давайте попробуем начать сначала. Введите /start",
        )
        return

    await onboarding.process_to_enter_login(user_id, text, state)


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.to_enter_password)
async def to_enter_password(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_enter_password"""
    user_id: int = message.from_user.id
    password: str = message.text

    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d provided password: ***. Status: %s", user_id, current_state
    )

    if message.is_command():
        await onboarding.process_cancel(
            user_id,
            state,
            "Что-то пошло не так? Давайте попробуем начать сначала. Введите /start",
        )
        return

    await onboarding.process_to_enter_password(user_id, password, state)


# TICKETS
# =======================================================


@dp.message_handler(commands=["tickets"], state=Form.logged_in)
async def list_all_tickets(message: types.Message, state: FSMContext) -> None:
    """Reacts on /tickets command in every state"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d issued /tickets command. State: %s", user_id, current_state
    )

    await generic.list_all_tickets(user_id=user_id, state=state)


@dp.message_handler(commands=["add"], state=Form.logged_in)
async def add_ticket(message: types.Message, state: FSMContext) -> None:
    """Reacts on /add command for logged user"""
    user_id: int = message.from_user.id
    current_state: Union[str, None] = await state.get_state()
    logging.info("User ID %d issued /add command. State: %s", user_id, current_state)

    await generic.add_new_ticket(user_id=user_id)


@dp.message_handler(content_types=types.ContentTypes.TEXT, state=Form.to_enter_title)
async def to_enter_title(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_enter_title"""
    user_id: int = message.from_user.id
    text = message.text

    await generic.process_to_enter_title(user_id=user_id, title=text, state=state)


@dp.message_handler(
    content_types=types.ContentTypes.TEXT, state=Form.to_enter_description
)
async def to_enter_description(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_enter_description"""
    user_id: int = message.from_user.id
    text = message.text

    await generic.process_to_enter_description(
        user_id=user_id, description=text, state=state
    )


@dp.message_handler(
    content_types=types.ContentTypes.TEXT, state=Form.to_select_priority
)
async def to_select_priority(message: types.Message, state: FSMContext) -> None:
    """Reacts on every text entered with the state Form.to_select_priority"""
    user_id: int = message.from_user.id
    text = message.text

    await generic.process_to_select_priority(
        user_id=user_id, priority=text, state=state
    )


# UNKNOWN input
# ===============================================================


@dp.message_handler(content_types=types.ContentTypes.TEXT, state="*")
async def text_message(message: types.Message, state: FSMContext) -> None:
    """Process any unhandled text messages"""
    user_id: int = message.from_user.id
    text: str = message.text

    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d provided unhandled text input: %s. Status: %s",
        user_id,
        text,
        current_state,
    )

    await generic.text_message(user_id)


@dp.message_handler(state="*")
async def non_text_message(message: types.Message, state: FSMContext) -> None:
    """Process any unhandled non-text messages"""
    user_id: int = message.from_user.id

    current_state: Union[str, None] = await state.get_state()
    logging.info(
        "User ID %d provided unhandled non-text input. Status: %s",
        user_id,
        current_state,
    )

    await generic.text_message(user_id)


if __name__ == "__main__":
    th = threading.Thread(target=checker.my_thread_func)
    th.start()
    logging.info("GLPI Telegram bot is started")
    while True:
        try:
            executor.start_polling(dp, skip_updates=True)
        except NetworkError:
            logging.error("Network Error. Restarting...")
            continue
        else:
            break

    logging.info("GLPI Telegram bot is closed")
    config.WE_ARE_CLOSING = True
    th.join()
