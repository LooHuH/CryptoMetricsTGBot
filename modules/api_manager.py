import requests as r

from modules.config import API_TOKEN


class CoinStatsAPI:
    name = 'CoinStats'
    BASE_URL = "https://openapiv1.coinstats.app/"
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_TOKEN
    }

    def __build_request(self, *args, params: dict = None) -> str:
        url = self.BASE_URL + '/'.join(args)
        if params:
            url += '?' + '&'.join([f"{key}={item}" for key, item in params.items()])
        return url

    @staticmethod
    def __convert_response(response):
        response_json = response.json()
        if 'statusCode' in response_json:
            if response_json['statusCode'] == 400 or response_json['statusCode'] == 401:
                return None
        else:
            return response_json

    def __get_json_response(self, *args, params: dict = None, from_result: bool = False):
        resp = r.get(
            self.__build_request(*args, params=params),
            headers=self.headers
        )
        resp_json = self.__convert_response(resp)
        if from_result and ('result' in resp_json):
            return resp_json['result']
        else:
            return resp_json

    def get_coin_data(self, coin_id: str):
        return self.__get_json_response(
            'coins', coin_id
        )

    def get_coins(self, limit: int):
        return self.__get_json_response(
            'coins',
            params={
                'limit': limit
            },
            from_result=True
        )

    def get_coin_charts(self, coin_id: str, period: str):
        return [
            period,
            self.__get_json_response(
                'coins', coin_id, 'charts',
                params={'period': period}
            )
        ]
