statistics_fields = {
    'name', 'spent', 'impressions', 'clicks',
    'join_rate', 'effective_cost_per_click',
    'effective_cost_per_mille', 'effective_cpf',
}
stats_template ="""Статистика за период 😉
'name

Расход: 'spent ₽

Показы: 'impressions
Клики: 'clicks
Вступления: 'join_rate будет позже
CPC: 'effective_cost_per_click ₽
CPM: 'effective_cost_per_mille ₽
CPF: 'effective_cpf будет позже
"""

start_text = 'Привет! Я Стив - Ваш персональный бот-помощник!\nЯ могу показать статистику\nДальше дописать согласованный и продажный текст\nБлаБла'

permissions_update = txt = 'Ваши права изменены\nНеобходимо написать `/start` для обновления интерфейса'

start_chatting = 'Что у Вас случилось? Напишите любой вопрос и я передам его людям)'

accounts_rename_dict = {
    "Кабинет агентства #1": "1",
    "Кабинет агентства #2": "2",
    "Кабинет агентства #3": "3",
    "Кабинет агентства #4": "4",
    "Кабинет агентства #5": "5",

}
clients_rename_dict = {
    "elamadodomrv@gmail.com": "Минеральные Воды",
    "elamadodoptg@gmail.com": "Пятигорск",
    "elamadodonev@gmail.com": "Невинномысск",
    "dodoizhevsk-sarapul@yandex.ru": "Ижевск/Сарапул",
}

before_question = "Потратьте время просто так"
questions = (
    "Вопрос 1",
    "Вопрос 2",
    "Вопрос 3",
    "Вопрос 4",
)
after_question = "Спасибо, что потратили свое время впустую"

answers = (
    (
        "Ответ 1",
        "Ответ 2",
        "Ответ 3",
        "Ответ 4",
    ),
    (
        "Ответ 11",
        "Ответ 22",
        "Ответ 33",
        "Ответ 44",
    ),
    (
        "Ответ 12",
        "Ответ 23",
        "Ответ 34",
        "Ответ 45",
    ),
    (
        "Ответ 13",
        "Ответ 24",
        "Ответ 35",
        "Ответ 46",
    ),
)
