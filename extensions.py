from resources.questions import questions, answers  # Просто беру все вопросы и ответы
import smtplib  # Библиотека, чтобы посылать письма
from config import EMAIL, EMAIL_PASSWORD, CONTACT_EMAIL  # Все связанное с почтой
from email.message import EmailMessage  # Чтобы посылать письма с изображениями и в целом их посылать лучше так

# "Словарь" для хранения пользователей
user_list = {}


# Список животных не был задан в условии задания, выбрал на свое усмотрение животных, немного поправив под вопросы
# все животные выбраны с https://moscowzoo.ru/about/guardianship/waiting-guardianship поскольку викторина должна быть
# связана с системой опеки


class APIException(Exception):  # Просто класс ошибки
    pass


# Этот класс нужен чтобы множество пользователей могли использовать бота одновременно,
# он хранит свой счетчик для вопросов, свой список животных и хранится по id чата в словаре,
# в настоящей работе бота бы пришлось иногда перезапускать, чтобы очистить словарь пользователей

class User:
    def __init__(self):
        self.counter = 0  # Счетчик на каком вопросе
        # "Словарь" животных, цифра это то сколько балов набрано для него, ответом потом будет тот у кого баллов выше
        # так как это словарь то значения будут одинаковые во всех файлах
        self.animal_list = {"сиамский крокодил": 0, "снежный барс": 0, "альпака": 0, "медоед": 0, "морж": 0,
                            "ушастая сова": 0, "лучистая черепаха": 0}

    def add_counter(self):
        self.counter += 1

    # Метод для начисления очков животным
    def give_points(self, ans, list_ans):
        for i in range(len(ans[list_ans])):
            # Даю им очко если ответ подходит к животному
            self.animal_list[ans[list_ans][i]] += 1


# Класс для викторины
class Quiz:
    # Получаю вопрос и ответ
    @staticmethod
    def get_question(i):
        text = questions[i]
        answer = answers[i]
        return text, answer


class MailSender:
    def __init__(self):
        self.smtpObj = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        self.smtpObj.login(EMAIL, EMAIL_PASSWORD)

    def send(self, result, first_name, last_name):
        msg = EmailMessage()
        msg['Subject'] = "Вопрос о программе опеки"
        msg['From'] = EMAIL
        msg['To'] = CONTACT_EMAIL
        msg.set_content(f"{first_name} {last_name} получил результат {result} и теперь интересуется в программе опеки "
                        f"и имеет несколько вопросов о программе, вскоре от него должно поступить письмо.")
        with open(f'resources/{result}.jpg', 'rb') as photo:
            img_data = photo.read()
        msg.add_attachment(img_data, maintype="image", subtype="jpeg")
        self.smtpObj.send_message(msg)
        msg.set_content(" ")

    def send_feedback(self, first_name, last_name, feedback):
        msg = EmailMessage()
        msg['subject'] = "Обратная связь о работе бота"
        msg['From'] = EMAIL
        msg['To'] = CONTACT_EMAIL
        msg.set_content(f"{first_name} {last_name} посылает обратную связь о работе бота:\n{feedback}")
        self.smtpObj.send_message(msg)
        msg.set_content(" ")
