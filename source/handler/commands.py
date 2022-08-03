import asyncio

from source.bot import *
from aiogram import types

from source.parser import *
from source.users import *
from source.texts import *
from source.keyboard import *
from source.base.companiesbase import *


@dp.callback_query_handler()
async def new_button(event: types.CallbackQuery):
    id = event.from_user.id
    command = event.data
    print(id, command)

    if 'stop' == command:
        add_button.discard(id)
        change_admin.discard(id)
        change_client.discard(id)
        update(id, 'button_id', 0, 'users')
        # old = await bot.delete_message(event.from_user.id, event.message.message_id)
        old = await event.message.edit_text('✅')
        await asyncio.sleep(3)
        await old.delete()

    elif command.startswith('get'):  # TODO
        userId, mode = map(int, command.split('=')[1:])
        try:
            time = 'today'
            match mode:
                case 0:  # вчера
                    time = 'yesterday'
                case 1:  # сегодня
                    time = 'today'
                case 2:  # неделя
                    time = 'week'
                case 3:  # 2 недели
                    time = '2week'
                case 4:  # месяц
                    time = 'month'
            cur_settings = users_get_company(userId)
            for account_id in cur_settings:
                ids = cur_settings[account_id]
                for client_id in ids:
                    data = client_get_stats(int(account_id), int(client_id), time)
                    await bot.send_message(id, data)
                    asyncio.sleep(2.5)
        except IndexError:
            await bot.send_message(id, 'Нет данных за этот период')
        except Exception as e:
            print(e)
            await bot.send_message(id, 'Администратор пока не настроил вам кабинет\n')

    elif command.startswith('addAccountId'):
        values = command.split('=')[1:]
        values = values + [len(values)]
        match values:
            case 0,:
                add_accountId[id] = [-1, ]
                await event.message.edit_text('Введите ID пользователя')
                await event.message.edit_reply_markup(back_to_settings_button)
            case userId, 1:
                userId = users_get(userId)
                if not userId:
                    await event.message.delete()
                    await bot.send_message(id, 'Аккаунт не найден')
                else:
                    add_accountId[id][0] = userId['id']
                    await event.message.edit_text('Выберите accountId пользователя')
                    await event.message.edit_reply_markup(make_client_accounts_buttons(userId['id']))
            case userId, accountId, 2:
                await event.message.edit_text(f'Выберите кабинет')
                await event.message.edit_reply_markup(make_client_list_accounts_buttons(userId, accountId))
            case userId, accountId, clientId, 3:
                userId = users_get(userId)
                if not userId:
                    await event.message.delete()
                    await bot.send_message(id, 'Аккаунт не найден')
                else:
                    userId = userId['id']

                    cur = users_get_company(userId)
                    accountId = str(accountId)
                    clientId = int(clientId)
                    if accountId in cur:
                        if clientId in cur[accountId]:
                            cur[accountId].remove(clientId)
                            if len(cur[accountId]) == 0:
                                del cur[accountId]
                        else:
                            cur[accountId].append(clientId)
                    else:
                        cur[accountId] = [clientId]

                    update(userId, 'companies', json.dumps(cur), 'users')
                    await event.message.edit_reply_markup(make_client_list_accounts_buttons(userId, accountId))

    elif command.startswith('showAccounts'):
        txt, data = accounts_get_list()
        await event.message.edit_text(txt, reply_markup=make_clientIds_buttons(data), parse_mode='markdown')

    elif command.startswith('showClients'):
        accountId = command.split('=')[1:][0]
        txt = clients_get_list(accountId)
        await bot.send_message(id, txt, parse_mode='markdown')

    elif command.startswith('contact'):
        userId, = map(int, command.split('=')[1:])
        userForwardId = users_forward_id(userId)
        if userForwardId == -1 or userForwardId == 0:
            update(userId, 'forward_id', id, 'users')
            update(id, 'forward_id', userId, 'users')
            await bot.send_message(id, 'Включен режим диалога', reply_markup=chat_keyboard)
            await bot.send_message(userId, 'Включен режим диалога', reply_markup=chat_keyboard)
        else:
            await bot.send_message(id, 'У пользователя уже имеется незавершенный диалог')

    elif command.startswith('changeParser'):
        values = command.split('=')[1:]
        values = list(map(int, values)) + [len(values)]
        match values:
            case 0:
                pass

    elif command.startswith('quest'):
        idx, answerIdx = map(int, command.split('=')[1:])
        users_add_answer(id, answerIdx)
        if idx < len(questions):
            txt, markup = questions[idx], make_questions_buttons(idx)
            await event.message.edit_text(txt)
            await event.message.edit_reply_markup(markup)
        else:
            await event.message.delete()
            await bot.send_message(id, after_question)

    elif command.startswith('changeRole'):
        values = command.split('=')[1:]
        values = list(map(int, values)) + [len(values)]
        match values:
            case idx, 1:
                if idx == 0:
                    change_client.add(id)
                elif idx == 1:
                    change_admin.add(id)
                await event.message.edit_text('Введите ID устройства')
                await event.message.edit_reply_markup(back_to_settings_button)
            case idx, deviceId, 2:
                txt = 'Права изменены'
                if idx == 0:
                    change_client.discard(id)
                    flag = users_is_client(deviceId)
                    update(deviceId, 'is_client', (flag + 1) % 2, 'users')
                    try:
                        await bot.send_message(deviceId, permissions_update)
                    except Exception as e:
                        logging.error(str(e))
                elif idx == 1:
                    change_admin.discard(id)
                    if deviceId != mainAdmin and deviceId != id:
                        flag = users_is_admin(deviceId)
                        update(deviceId, 'is_admin', (flag + 1) % 2, 'users')
                        try:
                            await bot.send_message(deviceId, permissions_update)
                        except Exception as e:
                            logging.error(str(e))
                    else:
                        txt = 'Запрещено изменять права администратора у данного пользователя'
                await event.message.edit_text(txt)
                await event.message.edit_reply_markup(settings_buttons)

    elif command == 'settings':
        add_button.discard(id)
        update(id, 'button_id', 0, 'users')
        change_client.discard(id)
        change_admin.discard(id)
        if id in add_accountId:
            del add_accountId[id]
        txt = '⚙Выберите необходимый пункт'
        await event.message.edit_text(txt)
        await event.message.edit_reply_markup(settings_buttons)
