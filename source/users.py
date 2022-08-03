import asyncio
from source.base.userbase import *
from source.keyboard import *
from source.bot import *

add_button = set()

change_client = set()
change_admin = set()
add_accountId = dict()


def right_keyboard(id):
    if users_is_admin(id):
        return admin_keyboard
    if users_is_client(id):
        return client_keyboad
    return main_keyboard


async def new_notification(id, text, user_info):
    for person in users_get_admins():

        await bot.send_message(
            person['id'],
            text + f'\n\n{user_info}',
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton('Написать', callback_data=f'contact={id}')]
            ]),
            parse_mode='markdown'
        )

async def send_first_questions():
    for user in users_get_clients():
        users_clear_answer(user['id'])
        await bot.send_message(
            user['id'],
            before_question + '\n' + questions[0],
            reply_markup=make_questions_buttons(0),
            parse_mode='markdown'
        )


async def questions_sendler():
    print('Запуск вопросов')
    while True:
        now = datetime.now()

        if now.day == 28:
            await send_first_questions()

        print('Отправка закончена')
        await asyncio.sleep(86400)


async def calculate_csi():
    answer = ''
    for user in users_get_all():
        answer += users_get_answer(user['id']) + '\n'
    return answer
