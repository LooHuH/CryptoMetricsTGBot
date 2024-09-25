import requests

import asyncio
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup

from modules.data import Vars


def user_from(source):
    return source.from_user.id


async def delete_user_info(user_id: int):
    user = Vars.users[user_id]
    Vars.users.pop(user_id)
    try:
        await user.start_message.delete()
        await user.menu_message.delete()
        await user.temp_message.delete()
    except Exception:
        pass


async def answer_and_delete(
        message: Message,
        delete_after: int,
        text: str,
        reply_markup: ReplyKeyboardMarkup = None
):
    temp_message = await message.answer(
        text=text,
        reply_markup=reply_markup
    )
    await asyncio.sleep(delete_after)
    await temp_message.delete()


def download_image(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        return open('assets/unknown.png', 'rb')


def convert_to_currency(
        value,
        currency: str = '$',
        thousand_separator: str = ',',
        float_separator: str = '.'
):
    value_split = str(format(value, '.16f')).split('.')
    main_part = None
    float_part = None
    if len(value_split) > 1:
        main_part = value_split[0]
        float_part = value_split[1]
    else:
        main_part = value_split
    main_part_int = int(main_part)
    main_part_len = len(main_part)
    if main_part_len > 1:
        for i in range(main_part_len):
            index = main_part_len - i
            if (i % 3 == 0
                    and index != main_part_len):
                main_part = main_part[:index] + thousand_separator + main_part[index:]
    if float_part is not None:
        if main_part_int < 1:
            counter = 0
            for i in range(len(float_part)):
                if counter >= 5:
                    float_part = float_part[:i]
                    break
                if float_part[i] != '0':
                    counter += 1
                else:
                    if counter >= 3:
                        float_part = float_part[:i]
                        break
                    if counter > 1:
                        float_part = float_part[:i + 3]
                        break
        if main_part_int >= 1:
            float_part = float_part[:3]
        if main_part_int >= 10:
            float_part = float_part[:2]
    output = currency + main_part
    if float_part is not None:
        output += float_separator + float_part

    return output

    