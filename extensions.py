import redis
import json
import requests
import datetime

import config

CURRENCIES_ENUM = {j: i for i, j in zip(config.CURRENCIES, config.CURRENCIES.values())}


class APIException(Exception):
    pass


class ConvertException(APIException):
    pass


class NoAccessException(APIException):
    pass


class CurrencyConverter:
    @staticmethod
    def get_currency_api(currency_from: str):
        req = requests.get(f"https://api.exchangeratesapi.io/latest?base={currency_from}")
        if req.status_code == 200:
            return req.content
        else:
            raise NoAccessException(f'Проблемы с сервером курсов валют: {req.status_code}')

    @staticmethod
    def get_price(base: str, quote: str, amount: float):

        red = redis.Redis(host=config.REDIS_ACC['host'], port=config.REDIS_ACC['port'],
                          password=config.REDIS_ACC['password'])
        if not red:
            raise NoAccessException(f'Проблемы с сервером кэширования')

        red_today = json.loads(red.get('today'))
        if not red_today or (red_today != datetime.date.today().isoformat()):
            red_record = CurrencyConverter.get_currency_api(base)
            red.set(base, red_record)
            currency_rates = json.loads(red_record)
            red.set('last_date', json.dumps(currency_rates['date']))
            red_last_date = currency_rates['date']
            red.set('today', json.dumps(datetime.date.today().isoformat()))
        else:
            red_last_date = json.loads(red.get('last_date'))
            red_record = red.get(base)

        if red_record:
            currency_rates = json.loads(red_record)
            if currency_rates['date'] == red_last_date:
                return currency_rates['rates'][quote] * amount

        api_res = CurrencyConverter.get_currency_api(base)
        red.set(base, api_res)
        currency_rates = json.loads(api_res)
        return currency_rates['rates'][quote] * amount

    @staticmethod
    def currency_enum(conv_list: list):
        if conv_list[0].upper() in config.CURRENCIES:
            currency = conv_list.pop(0)
        elif conv_list[0] in CURRENCIES_ENUM:
            currency = CURRENCIES_ENUM[conv_list.pop(0)]
        elif ' '.join(conv_list[:2]) in CURRENCIES_ENUM:
            currency = CURRENCIES_ENUM[' '.join(conv_list[:2])]
            conv_list.pop(0)
            conv_list.pop(0)
        elif ' '.join(conv_list[:3]) in CURRENCIES_ENUM:
            currency = CURRENCIES_ENUM[' '.join(conv_list[:3])]
            conv_list.pop(0)
            conv_list.pop(0)
            conv_list.pop(0)
        else:
            raise ConvertException(f'Не удалось обработать валюту: {conv_list[0]}')
        return currency.upper()

    @staticmethod
    def convert_currency_str(conv_string: str):
        conv_list = conv_string.lower().split()
        currency_from = CurrencyConverter.currency_enum(conv_list)
        currency_to = CurrencyConverter.currency_enum(conv_list)

        if conv_list:
            try:
                amount = float(conv_list[0])
            except ValueError:
                raise ConvertException(f'Не удалось обработать количество: {conv_list[0]}')
        else:
            amount = 1

        rate = CurrencyConverter.get_price(currency_from, currency_to, amount)

        return currency_from, currency_to, amount, rate
