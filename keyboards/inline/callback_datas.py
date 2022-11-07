from aiogram.utils.callback_data import CallbackData


choose_language_callback = CallbackData("lang_", "language")
choose_channel_callback = CallbackData("channel_",
                                       "channel",
                                       "channel_id")
choose_subscribe_callback = CallbackData("subscribe_",
                                         "subscribe_period",
                                         "subscribe_price")
