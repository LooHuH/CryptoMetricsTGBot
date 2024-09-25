from aiogram import types

from modules.api_manager import CoinStatsAPI


class ButtonList:
    def __init__(self):
        self.__current_page = 1
        self.pages = dict()

    def __len__(self):
        return len(self.pages)

    def current_page(self, page_num: int = None, output: bool = False):
        if page_num:
            if 1 <= page_num <= len(self):
                self.__current_page = page_num
                if output:
                    return self.__current_page, self.pages[self.__current_page]
            else:
                raise IndexError
        else:
            return self.__current_page, self.pages[self.__current_page]

    def next_page(self):
        if self.__current_page < len(self):
            self.__current_page += 1

    def prev_page(self):
        if self.__current_page > 1:
            self.__current_page -= 1

    @staticmethod
    def button_sort(coins_list):
        coins_sorted = []
        for i in range(len(coins_list) // 2):
            coins_sorted.append(coins_list[i])
            coins_sorted.append(coins_list[i + len(coins_list) // 2])
        return coins_sorted


class CoinList(ButtonList):
    def __init__(self, items_on_one_page: int, pages: int):
        super().__init__()
        self.api = CoinStatsAPI()
        self.list = self.api.get_coins(limit=(items_on_one_page * pages))
        for i in range(pages):
            self.pages[i + 1] = self.list[i * items_on_one_page: (i + 1) * items_on_one_page]
        for page in self.pages:
            page_list = self.button_sort(self.pages[page])
            page_dict = dict()
            for coin in page_list:
                page_dict[coin['id']] = coin
            self.pages[page] = page_dict

    def find(self, coin_id):
        for coin in self.list:
            if coin_id in coin['id']:
                return coin
        return None


class UserInteractionInfo:
    def __init__(self):
        self.start_message: types.Message = None
        self.menu_message: types.Message = None
        self.temp_message: types.Message = None
        self.chosen_coin_data: dict = None
        self.chosen_coin_charts_data: list = None
        self.coin_list: CoinList = None


periods_list = ButtonList.button_sort([
    {
        'name': '24 hours',
        'id': '24h'
    },
    {
        'name': '1 week',
        'id': '1w'
    },
    {
        'name': '1 month',
        'id': '1m'
    },
    {
        'name': '3 months',
        'id': '3m'
    },
    {
        'name': '1 year',
        'id': '1y'
    },
    {
        'name': 'All time',
        'id': 'all'
    }
])
