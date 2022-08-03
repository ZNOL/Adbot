import asyncio

from source.bot import *
from source.texts import *
from source.parser import *
from source.users import *
from aiogram import types


@dp.message_handler()
async def new_message(message: types.Message):
    id = message.from_user.id
    text = message.text

    print(id, text)
    print(message.from_user)
    if '/start' == text:
        if not users_get(id):
            if id == mainAdmin:
                users_add(id, 1, 1)
            else:
                users_add(id)
            await bot.send_message(
                mainAdmin,
                f'Новый пользователь (`{id}`) @{message.from_user.username}',
                parse_mode='markdown'
            )

        update(id, 'forward_id', 0, 'users')

        await message.delete()
        await bot.send_message(id, start_text, reply_markup=right_keyboard(id))

    elif 'Получить показатели 📊' == text:
        await message.delete()
        await bot.send_message(id, 'Выберите временной интервал', reply_markup=make_indicators_buttons(id))

    elif 'Связаться 📞' == text:
        await message.delete()
        update(id, 'forward_id', -1, 'users')
        await bot.send_message(id, start_chatting, reply_markup=chat_keyboard)

    elif 'Завершить диалог☎️' == text:
        await message.delete()

        forwardId = users_forward_id(id)
        try:
            if users_forward_id(forwardId) != id:
                raise ValueError

            update(forwardId, 'forward_id', 0, 'users')
            await bot.send_message(forwardId, 'Собеседник завершил диалог', reply_markup=right_keyboard(forwardId))
        except Exception as e:
            logging.error(str(e))

        update(id, 'forward_id', 0, 'users')
        await bot.send_message(id, 'Вы можете продолжать пользоваться ботом', reply_markup=right_keyboard(id))

    elif 'Настройки ⚙' == text and users_is_admin(id):
        await bot.send_message(id, 'Выберите пункт', reply_markup=settings_buttons)

    elif text.startswith('/nick') and users_is_admin(id):
        if len(text.split()) == 3:
            userId, nickname = text.split()[1:]
            userId = users_get(userId)

            print(userId)
            if not userId:
                await bot.send_message(id, 'Пользователь не найден')
            else:
                update(userId['id'], 'nickname', nickname, 'users')

                userId = users_get(userId['id'])

                await bot.send_message(id, f'Для пользователя установлен логин: "{userId["nickname"]}"')
        else:
            await bot.send_message(id, 'Неверный формат')


    elif 'CSI📊' == text and users_is_admin(id):
        answer = await calculate_csi()
        await bot.send_message(id, answer)

    elif id in change_client and users_is_admin(id):
        await message.delete()
        try:
            deviceId = int(text)
            flag = users_is_client(deviceId)
            if flag is None:
                raise ValueError
            txt = f'Клиент: {"✅" if flag else "❌"}'
            await bot.send_message(id, txt, reply_markup=make_permissions_change_buttons(0, deviceId))
        except ValueError:
            await bot.send_message(id, 'Пользователь не найден\nПовторите отправку ID',
                                   reply_markup=back_to_settings_button)

    elif id in change_admin and users_is_admin(id):
        await message.delete()
        try:
            deviceId = int(text)
            flag = users_is_admin(deviceId)
            if flag is None:
                raise ValueError
            txt = f'Админ: {"✅" if flag else "❌"}'
            await bot.send_message(id, txt, reply_markup=make_permissions_change_buttons(1, deviceId))
        except ValueError:
            await bot.send_message(id, 'Пользователь не найден\nПовторите отправку ID',
                                   reply_markup=back_to_settings_button)

    elif id in add_accountId and users_is_admin(id):
        await message.delete()
        if add_accountId[id][0] == -1:
            userId = text
            add_accountId[id][0] = userId
            await bot.send_message(id, f'Изменить настройки для пользователя {userId}?',
                                   reply_markup=make_accountId_buttons(userId)
            )

    elif '/get_id' == text:
        await message.delete()
        old = await bot.send_message(id, f'Ваш 🆔: `{id}`', parse_mode='markdown')
        await asyncio.sleep(15)
        await old.delete()

    elif '/start_send' == text:
        await message.delete()
        await send_first_questions()

    else:
        match users_forward_id(id):
            case 0:
                pass
            case -1:
                user_info = f'ID `{message.from_user.id}` @{message.from_user.username} '\
                            f'{message.from_user.first_name} {message.from_user.last_name}'
                await new_notification(id, text, user_info)
            case forwardId:
                text += f'\n {message.from_user.first_name} {message.from_user.last_name}'
                await bot.send_message(forwardId, text)
