import config
import redis

CURRENCIES_ENUM = {j: i for i, j in zip(config.CURRENCIES, config.CURRENCIES.values())}


class ConvertException(Exception):
    pass


class CurrencyConverter:
    @staticmethod
    def get_currency_rate(currency_from: str, currency_to: str):
        pass

    @staticmethod
    def currency_enum(conv_list: list):
        if conv_list[0] in config.CURRENCIES:
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
            raise ConvertException(f'Не удалось обработать валюту {conv_list[0]}')
        return currency

    @staticmethod
    def convert_currency(conv_string: str):
        conv_list = conv_string.lower().split()
        currency_from = CurrencyConverter.currency_enum(conv_list)
        currency_to = CurrencyConverter.currency_enum(conv_list)

        try:
            amount = float(conv_list[0])
        except ValueError:
            raise ConvertException(f'Не удалось обработать количество {conv_list[0]}')

        print(currency_from, currency_to, amount)


