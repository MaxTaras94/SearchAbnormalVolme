from loader import dp
from aiogram.types import CallbackQuery, Message, User
from aiogram.dispatcher import FSMContext
from aiogram.utils.markdown import hlink
from states.newsubscribe import NewSubscribeStates
from keyboards.inline.choose_subscribe import choose_subscribe
from utils.db_api.db_commands import database


@dp.callback_query_handler(text_contains="channel_",
                           state=NewSubscribeStates.Q1)
async def channel1(call: CallbackQuery, state: FSMContext):
    """
    Обрабатываем выбор канала через inline кнопки.
    """
    await call.answer(cache_time=10)
    subscribe_channel = call.data.split(':')[1]
    subscribe_channel_id = call.data.split(':')[2]

    # Проверяем есть ли уже подписка на этот канал
    user = User.get_current()
    chat_id = user.id

    user_subscribe = await database.get_user_subscribe(
        chat_id=chat_id,
        subscribe_channel_id=subscribe_channel_id)

    if user_subscribe is not None:
        text = "Продление подписки на канал\n"
        text += f"<b>{subscribe_channel}</b>\n\n"
        text += "Выберите срок продления:"
        await state.update_data(subscribe_status="Update")
        await state.update_data(subscribe_id=user_subscribe["id"])
        await state.update_data(
            subscribe_channel_link=user_subscribe["channel_link"])
        await state.update_data(
            subscribe_start_time=user_subscribe["start_time"])
        await state.update_data(
            subscribe_paid_till=user_subscribe["paid_till"])
    else:
        text = "Подписка на канал\n"
        text += f"<b>{subscribe_channel}</b>\n\n"
        text += "Выберите срок подписки:"
        await state.update_data(subscribe_status="Booking")

    await state.update_data(chat_id=chat_id)
    await state.update_data(subscribe_channel=subscribe_channel)
    await state.update_data(subscribe_channel_id=subscribe_channel_id)
    await call.message.edit_text(text=text,
                                 reply_markup=choose_subscribe)
    await NewSubscribeStates.Q2.set()


@dp.message_handler(state=NewSubscribeStates.Q1)
async def channel2(message: Message, state: FSMContext):
    """
    Выбрать канал можно только через inline кнопки.
    Если приходит какой-то текст - просим кликнуть на кнопки с каналами.
    """
    pass
