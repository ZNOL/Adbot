from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from source.base.buttonsbase import *
from source.base.userbase import *
from source.parser import *
from source.texts import *

main_keyboard_template = [
    [
        KeyboardButton('Связаться 📞'),
    ],
]
main_keyboard = ReplyKeyboardMarkup(main_keyboard_template, resize_keyboard=True)

client_keyboad_template = [
    [
        KeyboardButton('Получить показатели 📊')
    ],
]
client_keyboad = ReplyKeyboardMarkup(client_keyboad_template + main_keyboard_template, resize_keyboard=True)

admin_keyboard_template = [
    [
        KeyboardButton('CSI📊'),
    ],
    [
        KeyboardButton('Настройки ⚙'),
    ],
]
admin_keyboard = ReplyKeyboardMarkup(
    client_keyboad_template + main_keyboard_template + admin_keyboard_template, resize_keyboard=True
)

chat_keyboard_template = [
    [
        KeyboardButton('Завершить диалог☎️')
    ]
]
chat_keyboard = ReplyKeyboardMarkup(chat_keyboard_template, resize_keyboard=True)

back_to_settings_button = InlineKeyboardMarkup(
    InlineKeyboardButton('Назад⏏️', callback_data='settings')
)

settings_buttons_template = [
#    [InlineKeyboardButton('Настроить парсер', callback_data='changeParser')],
    [InlineKeyboardButton('Получить ID доступных рекламных агентств', callback_data='showAccounts')],
    [InlineKeyboardButton('Добавить Account id пользователю', callback_data='addAccountId')],
    [InlineKeyboardButton('Добавить/удалить клиента', callback_data='changeRole=0')],
    [InlineKeyboardButton('Добавить/удалить агента', callback_data='changeRole=1')],
    [InlineKeyboardButton('Завершить', callback_data='stop')],
]
settings_buttons = InlineKeyboardMarkup(inline_keyboard=settings_buttons_template)


def make_permissions_change_buttons(idx, deviceId):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Изменить права', callback_data=f'changeRole={idx}={deviceId}')],
        [InlineKeyboardButton('Отмена', callback_data='settings')],
    ])


def make_indicators_buttons(id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton('Вчера', callback_data=f'get={id}=0'),
            InlineKeyboardButton('Сегодня', callback_data=f'get={id}=1'),
        ],
        [
            InlineKeyboardButton('Неделя', callback_data=f'get={id}=2'),
            InlineKeyboardButton('2 недели', callback_data=f'get={id}=3'),
        ],
        [
            InlineKeyboardButton('Месяц', callback_data=f'get={id}=4')
        ]
    ])


def make_accountId_buttons(id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton('Да✅', callback_data=f'addAccountId={id}'),
        ],
        [
            InlineKeyboardButton('Отмена❌', callback_data='settings'),
        ]
    ])


def make_clientIds_buttons(inp):
    seq = [[]]
    k = 0
    inRow = 3
    for accountId in inp:
        if k % inRow != 0:
            seq[-1].append(InlineKeyboardButton(f'{accountId}', callback_data=f'showClients={accountId}'))
        else:
            seq.append([
                InlineKeyboardButton(f'{accountId}', callback_data=f'showClients={accountId}')
            ])
        k = (k + 1) % inRow
    return InlineKeyboardMarkup(
        inline_keyboard=seq
    )


def make_client_accounts_buttons(userId):
    info = parse_accounts()
    seq = []
    for accountId in info:
        name = info[accountId]['account_name']
        if name in accounts_rename_dict:
            name = accounts_rename_dict[name]

        seq.append([
                InlineKeyboardButton(f"{name}",
                callback_data=f'addAccountId={userId}={accountId}')
    ])
    seq.append([InlineKeyboardButton('Отмена❌', callback_data='settings')])
    return InlineKeyboardMarkup(
        inline_keyboard=seq
    )


def make_client_list_accounts_buttons(userId, accountId):
    data = get_clients(accountId)
    cur = users_get_company(userId)
    seq = []
    for client in data:
        name = client['name']
        if name in clients_rename_dict:
            name = clients_rename_dict[name]

        txt = f"{name}"
        if str(accountId) in cur and int(client['id']) in cur[str(accountId)]:
            txt += '✅'
        else:
            txt += '❌'
        seq.append([
            InlineKeyboardButton(txt,
                                  callback_data=f"addAccountId={userId}={accountId}={client['id']}")
        ])
    seq.append([InlineKeyboardButton('Назад⏏️', callback_data=f"addAccountId={userId}")])
    return InlineKeyboardMarkup(
        inline_keyboard=seq
    )

def make_questions_buttons(idx):
    seq = []
    for i in range(len(answers[idx])):
        seq.append(
            [InlineKeyboardButton(answers[idx][i], callback_data=f'quest={idx + 1}={i}')]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=seq
    )
