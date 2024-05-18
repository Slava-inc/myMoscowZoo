from config import TOKEN
# Важное примечание: конфиг не имеет настоящих данных кроме токена и контактного email, их нужно заменить подходящими
import extensions
import telebot
from telebot import types  # для указания типов
# ссылка на бота: https://t.me/MosZooAnimalQuizBot

bot = telebot.TeleBot(TOKEN)
quiz = extensions.Quiz()
try:
    mail = extensions.MailSender()
except UnicodeEncodeError:
    print("Данные для почты не внесены в config.py,"
          " все функции с почтой (связь с сотрудником/обратная связь) не работают")


# Стартует всю викторину
@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    extensions.user_list[message.chat.id] = extensions.User()
    text = (f"Добро пожаловать на викторину 'Какое у вас тотемное животное?', викторина покажет вам ваше тотемное "
            "животное и после расскажет о программе опеки в Московском зоопарке.")
    bot.send_message(message.chat.id, text)
    ask(message)


# Сама викторина, поскольку функция трогает только сам телеграм её нельзя вынести в extensions
def ask(message: telebot.types.Message):
    if extensions.user_list[message.chat.id].counter >= len(extensions.questions):
        end(message)
        return
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
    que, ans = quiz.get_question(extensions.user_list[message.chat.id].counter)
    list_ans = list(ans)
    # У каждого вопроса по 4 ответа поэтому делаем 4 кнопки
    btn1 = types.KeyboardButton(list_ans[0])
    btn2 = types.KeyboardButton(list_ans[1])
    btn3 = types.KeyboardButton(list_ans[2])
    btn4 = types.KeyboardButton(list_ans[3])
    markup.add(btn1, btn2, btn3, btn4)
    bot.send_message(message.chat.id, f"Вопрос номер {extensions.user_list[message.chat.id].counter + 1}:")
    bot.send_message(message.chat.id, que.format(message.from_user), reply_markup=markup)


def end(message: telebot.types.Message):
    # Получаю животное с наибольшим числом баллов
    markup_inline = types.InlineKeyboardMarkup(row_width=1)
    button_repeat = types.InlineKeyboardButton(text="Повторить викторину", callback_data="repeat")
    button_info = types.InlineKeyboardButton(text="Узнать больше о программе опеки", callback_data="adoption")
    button_feedback = types.InlineKeyboardButton(text="Отправить обратную связь о работе бота",
                                                 callback_data="feedback")
    button_share = types.InlineKeyboardButton(text="Поделиться результатом", callback_data="share")
    markup_inline.add(button_info, button_repeat, button_feedback, button_share)
    result = max(extensions.user_list[message.chat.id].animal_list,
                 key=extensions.user_list[message.chat.id].animal_list.get)
    text = f"Поздравляю {message.chat.first_name}! Вы {result}!"
    # Открываю фото животного используя результат,
    # собственно фотографии называются так же как и животные и имеют .jpg формат
    with open(f"resources/{result}.jpg", "rb") as photo:
        bot.send_photo(message.chat.id, photo, caption=text, reply_markup=markup_inline)


# Обработчик для кнопок в конце
@bot.callback_query_handler(func=lambda call: True)
def end_buttons(call):
    if call.data == 'repeat':  # Если выбрано повторить викторину
        extensions.user_list[call.message.chat.id].counter = 0
        for value in extensions.user_list[call.message.chat.id].animal_list:
            extensions.user_list[call.message.chat.id].animal_list[value] = 0
        ask(call.message)
    elif call.data == "adoption":  # Если выбрано узнать больше информации о программы опеки
        markup_inline = types.InlineKeyboardMarkup(row_width=1)
        site_button = types.InlineKeyboardButton("Ссылка на программу опеки", url="https://moscowzoo.ru/about"
                                                                                  "/guardianship")
        reach_out_button = types.InlineKeyboardButton("Получить помощь с опекой от сотрудника зоопарка",
                                                      callback_data="reach_out")
        markup_inline.add(site_button, reach_out_button)
        bot.send_message(call.message.chat.id, "Программа опеки это программа в Московском зоопарке которая позволит"
                                               " вам за пожертвование любой суммы помочь внести свой вклад в развитие "
                                               "зоопарка и сохранения биоразнообразия планеты.\n Почётный статус "
                                               "опекуна позволяет круглый год навещать подопечного, быть в курсе "
                                               "событий его жизни и самочувствия, также ваше имя будет помещено в "
                                               "плашку рядом с вольером животного.\n"
                                               "Ваше тотемное животное будет очень радо любому пожертвованию от вас",
                         reply_markup=markup_inline)
    elif call.data == "reach_out":  # Если выбрано связаться с сотрудником зоопарка, доступно только после adoption
        reach_out_mail(call.message)
    elif call.data == "feedback":  # Если выбрана обратная связь
        msg = bot.send_message(call.message.chat.id, "Ваше следующее сообщение будет отправлено вместе с вашим именем "
                                                     "и фамилией на почту сотрудника зоопарка, спасибо за то что "
                                                     "предоставляете обратную связь о работе бота")
        bot.register_next_step_handler(msg, feedback_sender)
    elif call.data == "share":  # Если выбрано поделиться результатом, к сожалению копирует без изображения
        bot.send_message(call.message.chat.id, "Нажмите на сообщение чтобы его скопировать")
        result = max(extensions.user_list[call.message.chat.id].animal_list,
                     key=extensions.user_list[call.message.chat.id].animal_list.get)
        text = (f"`Мое тотемное животное это {result}!"
                f" Узнай свое тотемное животное при помощи бота https://t.me/MosZooAnimalQuizBot`")
        bot.send_message(call.message.chat.id, text, parse_mode="MARKDOWNV2")
    bot.answer_callback_query(callback_query_id=call.id)


# Отправка обратной связи на почту сотрудника
def feedback_sender(message: telebot.types.Message):
    text = message.text
    mail.send_feedback(message.chat.first_name, message.chat.last_name, text)
    bot.send_message(message.chat.id, "Ваше сообщение было отправлено, спасибо за обратную связь!")


# Функция для связи с сотрудником зоопарка
def reach_out_mail(message: telebot.types.Message):
    result = max(extensions.user_list[message.chat.id].animal_list,
                 key=extensions.user_list[message.chat.id].animal_list)
    mail.send(result, message.chat.first_name, message.chat.last_name)
    bot.send_message(message.chat.id, "Ваш результат вместе с вашим именем и фамилией был отправлен на почту "
                                      "сотрудника, пожалуйста напишите на почту SFHomeWorkMail@mail.ru используя ваше "
                                      "имя со всеми вашими вопросами")


# Это проверка вопроса и зачисление очков за вопрос.
@bot.message_handler(content_types=['text'])
def func(message: telebot.types.Message):
    ignore, ans = quiz.get_question(extensions.user_list[message.chat.id].counter)
    list_ans = list(ans)
    # Проверяем какой из 4 ответов был выбран, функция начислит очки животным которым подходит ответ Поскольку эта
    # функция работает каждый раз при сообщении нам надо повторить код с counter и ask в каждом elif а не отдельно
    if message.text == list_ans[0]:
        extensions.user_list[message.chat.id].give_points(ans, list_ans[0])
        extensions.user_list[message.chat.id].add_counter()
        ask(message)
    elif message.text == list_ans[1]:
        extensions.user_list[message.chat.id].give_points(ans, list_ans[1])
        extensions.user_list[message.chat.id].add_counter()
        ask(message)
    elif message.text == list_ans[2]:
        extensions.user_list[message.chat.id].give_points(ans, list_ans[2])
        extensions.user_list[message.chat.id].add_counter()
        ask(message)
    elif message.text == list_ans[3]:
        extensions.user_list[message.chat.id].give_points(ans, list_ans[3])
        extensions.user_list[message.chat.id].add_counter()
        ask(message)


bot.polling()
