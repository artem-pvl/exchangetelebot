import telebot

import config
import extensions

bot = telebot.TeleBot(config.BOT_TOKEN)


def main():
    bot.polling(none_stop=True)


@bot.message_handler(commands=["start"])
def handle_start(message: telebot.types.Message):
    txt_msg = f"Привет, {message.from_user.username}!\n" \
              f"Я бот калькулятор валют. Считаю из одной валюты в другую по курсу European Central Bank.\n" \
              f" Для помощи набери /help" \

    bot.send_message(message.chat.id, txt_msg)


@bot.message_handler(commands=["help"])
def handle_start(message: telebot.types.Message):
    txt_msg = "Для конвертации валют наберите <имя валюты цену которой вы хотите узнать> <имя валюты в которой надо " \
              "узнать цену первой валюты> <количество первой валюты>\n" \
              "Наименование валюты можно вводить названием (доллар сша рубль 100) или международным обозначением" \
              " (USD RUB 100)\n" \
              "/values - список валют\n" \
              "/help - это сообщение"

    bot.send_message(message.chat.id, txt_msg)


@bot.message_handler(commands=["values"])
def handle_start(message: telebot.types.Message):
    txt_cur = "\n".join([f"{config.CURRENCIES[i]} ({i}) - {config.COUNTRIES[i]}" for i in config.CURRENCIES])
    txt_msg = f'Список валют которые я умею считать:\n' \
              f'{txt_cur}'

    bot.send_message(message.chat.id, txt_msg)


@bot.message_handler(content_types=['text'])
def handle_start(message: telebot.types.Message):
    try:
        cur_from, cur_to, cur_amount, cur_rate = extensions.CurrencyConverter.convert_currency_str(message.text)
    except extensions.ConvertException as ex:
        bot.reply_to(message, f'{ex}')
    except extensions.APIException as ex:
        bot.reply_to(message, f'{ex}')
    else:
        msg_text = f"{round(cur_amount, 2)} {cur_from} = {round(cur_rate, 2)} {cur_to}"
        bot.reply_to(message, msg_text)


if __name__ == '__main__':
    main()
