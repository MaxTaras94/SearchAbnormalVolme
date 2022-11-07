import datetime
from dateutil import relativedelta
from loader import dp, bot
from aiogram import types
from aiogram.types import (CallbackQuery, Message,
                           LabeledPrice, PreCheckoutQuery,
                           SuccessfulPayment, ContentType)
from aiogram.dispatcher import FSMContext
from states.newsubscribe import NewSubscribeStates
from utils.db_api.db_commands import database


@dp.callback_query_handler(text_contains="subscribe_",
                           state=NewSubscribeStates.Q2)
async def subscribe1(call: CallbackQuery, state: FSMContext):
    """
    Обрабатываем выбор подписки через inline кнопки.
    """
    # user = types.User.get_current()
    # chat_id = user.id
    reg_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    await call.answer(cache_time=10)
    subscribe_period = call.data.split(':')[1]
    subscribe_price = int(call.data.split(':')[2])

    # await state.update_data(chat_id=chat_id)
    await state.update_data(reg_time=reg_time)
    await state.update_data(subscribe_period=subscribe_period)
    await state.update_data(subscribe_price=subscribe_price)
    data = await state.get_data()
    chat_id = int(data.get("chat_id"))
    subscribe_channel_id = int(data.get("subscribe_channel_id"))
    subscribe_channel = data.get("subscribe_channel")
    subscribe_status = data.get("subscribe_status")

    if subscribe_status == "Booking":
        text = f"Оформляем подписку на канал <b>{subscribe_channel}</b>\n"
        if subscribe_period == "month":
            text += "Срок подписки: <b>1 месяц</b>\n"
        else:
            text += "Срок подписки: <b>1 год</b>\n"
        text += f"Цена подписки: <b>{subscribe_price}$</b>\n\n"
        text += "Сразу после оплаты вам придёт уникальная ссылка "
        text += " для доступа в канал."
        await call.message.edit_text(text=text)

        title = f"{subscribe_channel} "
        description = f"Оплата подписки на канал {subscribe_channel} "
        if subscribe_period == "month":
            title += "1 месяц"
            description += "сроком на 1 месяц."
        else:
            title += "1 год"
            description += "сроком на 1 год."
        payload = "test"
        provider_token = "381764678:TEST:25546"
        start_parameter = "test"
        currency = "RUB"
        label = "Руб"
        # min 74,32 RUB
        amount = subscribe_price * 75 * 100
        prices = [LabeledPrice(label=label, amount=amount)]

        # Пишем данные в бд. Статус Booking
        await database.insert_newsubscribe(
            chat_id=chat_id,
            subscribe_channel_id=subscribe_channel_id,
            subscribe_channel=subscribe_channel,
            subscribe_period=subscribe_period,
            subscribe_price=subscribe_price,
            subscribe_status="Booking",
            payment_status="Invoice",
            payment_amount=amount,
            payment_currency=currency,
            provider_payment_charge_id="-",
            channel_link="-",
            start_time=reg_time,
            paid_till=reg_time,
            last_notify_time=reg_time,
            reg_time=reg_time
        )
        # Отправляем Invoice
        await bot.send_invoice(chat_id=chat_id,
                               title=title,
                               description=description,
                               payload=payload,
                               provider_token=provider_token,
                               start_parameter=start_parameter,
                               currency=currency,
                               prices=prices)

    if subscribe_status == "Update":
        text = f"Продлеваем подписку на канал <b>{subscribe_channel}</b>\n"
        if subscribe_period == "month":
            text += "Срок продления: <b>1 месяц</b>\n"
        else:
            text += "Срок продления: <b>1 год</b>\n"
        text += f"Цена продления: <b>{subscribe_price}$</b>\n\n"
        text += "Сразу после оплаты вам придёт уведомление "
        text += " о новом сроке вашей подписки."
        await call.message.edit_text(text=text)

        title = f"{subscribe_channel} "
        description = "Оплата продления подписки "
        description += f"на канал {subscribe_channel} "
        if subscribe_period == "month":
            title += "1 месяц"
            description += "сроком на 1 месяц."
        else:
            title += "1 год"
            description += "сроком на 1 год."
        payload = "test"
        provider_token = "381764678:TEST:25546"
        start_parameter = "test"
        currency = "RUB"
        label = "Руб"
        # min 74,32 RUB
        amount = subscribe_price * 75 * 100
        prices = [LabeledPrice(label=label, amount=amount)]

        # Отправляем Invoice
        await bot.send_invoice(chat_id=chat_id,
                               title=title,
                               description=description,
                               payload=payload,
                               provider_token=provider_token,
                               start_parameter=start_parameter,
                               currency=currency,
                               prices=prices)

    await NewSubscribeStates.Q3.set()


@dp.message_handler(state=NewSubscribeStates.Q2)
async def subscribe2(message: Message, state: FSMContext):
    """
    Выбор подписки только через inline кнопки.
    """
    pass


@dp.pre_checkout_query_handler(state=NewSubscribeStates.Q3)
async def checkout(query: PreCheckoutQuery, state: FSMContext):
    await bot.answer_pre_checkout_query(query.id, True)


@dp.message_handler(state=NewSubscribeStates.Q3)
async def subscribe3(message: Message, state: FSMContext):
    """
    Оплата только через inline кнопки.
    """
    pass


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT,
                    state=NewSubscribeStates.Q3)
async def successful_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    chat_id = int(data.get("chat_id"))
    reg_time = data.get("reg_time")
    subscribe_status = data.get("subscribe_status")
    subscribe_channel_id = int(data.get("subscribe_channel_id"))
    subscribe_channel = data.get("subscribe_channel")
    subscribe_period = data.get("subscribe_period")
    subscribe_price = data.get("subscribe_price")

    # id транзакции
    provider_payment_charge_id = message.successful_payment.provider_payment_charge_id

    if subscribe_status == "Booking":
        # формируем время paid_till
        start_time = datetime.datetime.now()
        if subscribe_period == "month":
            paid_till = start_time + relativedelta.relativedelta(months=+1)
        else:
            paid_till = start_time + relativedelta.relativedelta(months=+12)
    
        """!!! временно для теста !!!"""
        paid_till = start_time + relativedelta.relativedelta(minutes=+60)
    
        expire_date = int(datetime.datetime.timestamp(paid_till))
        # создаём уникальную ссылку
        channel_link = await bot.create_chat_invite_link(
            chat_id=subscribe_channel_id,
            member_limit=1,
            expire_date=expire_date)
        channel_link = channel_link["invite_link"]
        # Обновляем бд
        await database.update_newsubscribe(
            chat_id=chat_id,
            subscribe_status="Active",
            payment_status="Paid",
            provider_payment_charge_id=provider_payment_charge_id,
            channel_link=channel_link,
            start_time=start_time,
            paid_till=paid_till,
            reg_time=reg_time
            )
    
        text = "<b>Оплата прошла успешно!</b>\n\n"
        text += f"Вы оформили подписку на канал <b>{subscribe_channel}</b>\n"
        if subscribe_period == "month":
            text += "Срок подписки: <b>1 месяц</b>\n\n"
        else:
            text += "Срок подписки: <b>1 год</b>\n\n"
        text += f"Ваша ссылка для доступа в канал: {channel_link}"
        await message.answer(text=text)

    if subscribe_status == "Update":
        subscribe_id = int(data.get("subscribe_id"))
        subscribe_channel_link = data.get("subscribe_channel_link")
        subscribe_start_time = data.get("subscribe_start_time")
        subscribe_paid_till = data.get("subscribe_paid_till")

        # формируем новое время paid_till
        start_time = subscribe_paid_till
        if subscribe_period == "month":
            paid_till = start_time + relativedelta.relativedelta(months=+1)
        else:
            paid_till = start_time + relativedelta.relativedelta(months=+12)

        """!!! временно для теста !!!"""
        paid_till = start_time + relativedelta.relativedelta(minutes=+60)

        expire_date = int(datetime.datetime.timestamp(paid_till))
        # создаём уникальную ссылку
        channel_link = await bot.edit_chat_invite_link(
            chat_id=subscribe_channel_id,
            invite_link=subscribe_channel_link,
            member_limit=1,
            expire_date=expire_date)
        channel_link = channel_link["invite_link"]
        # Обновляем бд
        await database.update_subscribe(
            provider_payment_charge_id=provider_payment_charge_id,
            channel_link=channel_link,
            paid_till=paid_till,
            subscribe_id=subscribe_id
            )
    
        text = "<b>Оплата прошла успешно!</b>\n\n"
        text += f"Вы продлили подписку на канал <b>{subscribe_channel}</b>\n"
        if subscribe_period == "month":
            text += "Срок продления: <b>1 месяц</b>\n"
        else:
            text += "Срок продления: <b>1 год</b>\n"
        paid_till = paid_till.strftime("%Y-%m-%d %H:%M:%S")
        text += f"Теперь ваша подписка действует до <b>{paid_till}</b>\n\n"
        text += "Посмотреть все мои подписки\n"
        text += "<b>/mysubscribes</b>"
        await message.answer(text=text)

    await state.finish()
