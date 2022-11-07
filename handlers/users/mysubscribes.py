from loader import dp
from aiogram.types import CallbackQuery, Message, User
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from states.newsubscribe import NewSubscribeStates
from aiogram.utils.markdown import hlink
from keyboards.inline.choose_channel import choose_channel
from utils.db_api.db_commands import database


@dp.message_handler(Command("mysubscribes"), state="*")
async def mysubscribes(message: Message, state: FSMContext):
    """
    Показываем подписки пользователя.
    """
    await state.finish()
    await NewSubscribeStates.Q1.set()

    user = User.get_current()
    chat_id = user.id

    data = await database.get_user_subscribes(chat_id=chat_id)
    if len(data) > 0:
        text = "<b>Ваши подписки:</b>\n\n"
        for row in data:
            channel_id = int(str(row["subscribe_channel_id"])[4:])
            text += hlink(f"{row['subscribe_channel']}",
                          f"https://t.me/c/{channel_id}/1000000")
            text += "\n"
            text += "Старт с "
            text += f"<b>{row['start_time']}</b>\n"
            text += "Действует до "
            text += f"<b>{row['paid_till']}</b>\n"
            text += "Ваша персональная ссылка чтобы подписаться на канал "
            text += f"<b>{row['channel_link']}</b>\n\n"
        text += "Чтобы продлить или добавить новую подписку выберите канал:"
    else:
        text = "У вас нет активных подписок.\n\n"
        text += "Чтобы добавить новую подписку выберите канал:"

    await message.answer(text=text,
                         reply_markup=choose_channel)
