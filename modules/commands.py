from aiogram import Bot, Dispatcher, F 
from aiogram.types import Message, CallbackQuery, BufferedInputFile, BotCommand, BotCommandScopeDefault
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from modules.api_manager import CoinStatsAPI
from modules.objects import CoinList, periods_list, UserInteractionInfo
from modules.utils import user_from, answer_and_delete, delete_user_info
from modules.data import Vars
import modules.image_generator as image_generate


async def set_up(dp: Dispatcher, bot: Bot):
    commands = BotCommands(dp, bot)
    await bot.set_my_commands(commands.list, BotCommandScopeDefault())
    dp.startup.register(log_bot_start)
    dp.message.register(commands.start, Command(commands=['start']))
    dp.callback_query.register(commands.main_menu_callback_handler, F.data.startswith('main_menu_'))
    dp.callback_query.register(commands.coins_menu_callback_handler, F.data.startswith('coins_menu_'))


def log_bot_start():
    print('Bot started!')


class BotCommands:
    def __init__(self, dp: Dispatcher, bot: Bot):
        self.dp = dp
        self.bot = bot
        self.list = [
            BotCommand(
                command='start',
                description='Start menu'
            )
        ]

    async def start(self, message: Message):
        if message.from_user.id not in Vars.users:
            Vars.users[message.from_user.id] = UserInteractionInfo()
        await self.main_menu(message)

    @staticmethod
    async def main_menu(message: Message, start: bool = True):
        username = message.from_user.username
        mention = f'@{username}' if username is not None else 'random guy'
        if Vars.users[user_from(message)].menu_message is not None:
            try:
                await Vars.users[user_from(message)].start_message.delete()
                await Vars.users[user_from(message)].menu_message.delete()
            except Exception:
                pass
        if start:
            Vars.users[user_from(message)].start_message = message
        builder = InlineKeyboardBuilder()
        builder.button(
            text='💎 Coin info 💎',
            callback_data='main_menu_coins_menu'
        )
        builder.adjust()
        markup = builder.as_markup()
        Vars.users[user_from(message)].menu_message = await message.answer(
            text=f"Hi, {mention}! 👋\n"
                 f'🔽 Choose options from buttons below 🔽',
            reply_markup=markup
        )

    async def main_menu_callback_handler(self, callback: CallbackQuery):
        if callback.data == 'main_menu_coins_menu':
            await self.coins_menu(user_from(callback), reset_list=True)

    @staticmethod
    async def coins_menu(user_id: int, reset_list: bool = False, reset_menu: bool = True):
        if reset_list:
            Vars.users[user_id].coin_list = CoinList(items_on_one_page=8, pages=5)
        builder = InlineKeyboardBuilder()
        page_num, page = Vars.users[user_id].coin_list.current_page()
        builder.button(
            text='🔎 Search coin by ID',
            callback_data='coins_menu_search'
        )
        for coin_id in page:
            builder.button(
                text=f"#{page[coin_id]['rank']} {page[coin_id]['name']} ({page[coin_id]['symbol']})",
                callback_data=f"coins_menu_coin_{page[coin_id]['id']}"
            )
        builder.button(
            text='⏪ Prev',
            callback_data='coins_menu_prev'
        )
        builder.button(
            text=f'{page_num}/{len(Vars.users[user_id].coin_list)}',
            callback_data='coins_menu_pages'
        )
        builder.button(
            text='Next ⏩',
            callback_data='coins_menu_next'
        )
        builder.button(
            text='◀️ Back to main menu',
            callback_data='coins_menu_back'
        )
        sizes = [1, *[2 for _ in range(len(page) // 2)], 3, 1]
        builder.adjust(*sizes)
        markup = builder.as_markup()
        try:
            if reset_menu:
                await Vars.users[user_id].menu_message.edit_text(
                    text='👀 Please choose a coin from top list or search your coin 👀',
                    reply_markup=markup
                )
            else:
                await Vars.users[user_id].menu_message.edit_reply_markup(
                    reply_markup=markup
                )
        except Exception:
            pass

    async def coins_menu_callback_handler(self, callback: CallbackQuery):
        try:
            api = CoinStatsAPI()
            if callback.data == 'coins_menu_search':
                await self.coins_menu_call_search(api, callback)

            elif callback.data == 'coins_menu_next':
                Vars.users[user_from(callback)].coin_list.next_page()
                await self.coins_menu(user_from(callback))

            elif callback.data == 'coins_menu_prev':
                Vars.users[user_from(callback)].coin_list.prev_page()
                await self.coins_menu(user_from(callback))

            elif callback.data == 'coins_menu_pages':
                await self.coins_menu_ask_page(callback)

            elif callback.data == 'coins_menu_back':
                await self.main_menu(Vars.users[user_from(callback)].start_message)

            elif callback.data == 'coins_menu_sub_back':
                await self.coins_menu(user_from(callback), reset_menu=True)

            else:
                if 'page' in callback.data:
                    for num in range(1, 6):
                        if callback.data == f'coins_menu_page_{num}':
                            await Vars.users[user_from(callback)].temp_message.delete()
                            Vars.users[user_from(callback)].coin_list.current_page(page_num=num)
                            await self.coins_menu(user_from(callback))

                if 'period' in callback.data:
                    period = callback.data.replace('coins_menu_period_', '')
                    Vars.users[user_from(callback)].chosen_coin_charts_data = api.get_coin_charts(
                        coin_id=Vars.users[user_from(callback)].chosen_coin_data['id'],
                        period=period
                    )
                    await self.coins_menu_show_coin_info(callback)

                else:
                    coin_id = callback.data.replace('coins_menu_coin_', '')
                    if Vars.users[user_from(callback)].coin_list.find(coin_id):
                        Vars.users[user_from(callback)].chosen_coin_data = Vars.users[user_from(
                            callback)].coin_list.find(coin_id)
                        await self.coins_menu_ask_charts_period(user_from(callback))

        except KeyError:
            await callback.message.delete()
        except TypeError:
            await callback.message.delete()

    @staticmethod
    async def coins_menu_ask_page(callback: CallbackQuery):
        builder = InlineKeyboardBuilder()
        for num in range(1, 6):
            builder.button(
                text=str(num),
                callback_data=f'coins_menu_page_{num}'
            )
        markup = builder.as_markup()
        Vars.users[user_from(callback)].temp_message = await callback.message.answer(
            text=f'👀 Choose a page 👀',
            reply_markup=markup
        )

    async def coins_menu_call_search(self, api: CoinStatsAPI, callback: CallbackQuery):
        Vars.users[user_from(callback)].temp_message = await callback.message.answer(
            text=f'⌨️ Type coin ID from {api.name} ⌨️'
        )

        @self.dp.message()
        async def coins_menu_search_handle_message(message: Message):
            user_id = message.from_user.id
            coin = Vars.users[user_id].coin_list.find(message.text)
            if coin is None:
                coin = api.get_coin_data(message.text)
            if coin is not None:
                Vars.users[user_from(callback)].chosen_coin_data = coin
            else:
                await answer_and_delete(
                    message=message,
                    delete_after=3,
                    text='❗️ Coin not found ❗️',
                )
            await message.delete()
            await Vars.users[user_from(callback)].temp_message.delete()
            self.dp.message.handlers.pop()
            if coin is not None:
                await self.coins_menu_ask_charts_period(user_from(callback))

    @staticmethod
    async def coins_menu_ask_charts_period(user_id: int):
        builder = InlineKeyboardBuilder()
        for period in periods_list:
            builder.button(
                text=period['name'],
                callback_data=f"coins_menu_period_{period['id']}"
            )
        builder.button(
            text='◀️ Back to coins',
            callback_data='coins_menu_sub_back'
        )
        sizes = [*[2 for _ in range((len(periods_list) // 2) + 1)], 1]
        builder.adjust(*sizes)
        markup = builder.as_markup()
        coin_name = Vars.users[user_id].chosen_coin_data['name']
        await Vars.users[user_id].menu_message.edit_text(
            text=f'🕒 Choose a period for {coin_name} charts 🕒',
            reply_markup=markup
        )

    @staticmethod
    async def coins_menu_show_coin_info(callback: CallbackQuery):
        answer_image_raw = image_generate.coin_info(user_data=Vars.users[user_from(callback)])
        answer_image = BufferedInputFile(answer_image_raw, 'output')
        await callback.message.answer_photo(answer_image)
        await delete_user_info(user_from(callback))
