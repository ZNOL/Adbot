from source.base.base import *
import asyncio
from source.base.companiesbase import *
from source.parser import *
from datetime import datetime, time
from time import sleep


"""
0 ID
1 NAME
2 Расход
3 Показы
4 Клики
5 Переходы
6 CTR
7 eCPC
8 eCPM
9 на 1 штуку
"""

indexes_diff = {
    'Расход': 1,
    'Показы': 2,
    'Клики': 3,
    'Вступления': 4,
}
list_items = ['Расход', 'Показы', 'Клики', 'Вступления']
rows_idx = {
    'Бренд //': 9,
    'Акции //': 17,
    'Вступления //': 30,
    'Рассылка //': 38,
    'HR //': 46,
}


def determine_place(name):
    for i in rows_idx:
        if name.startswith(i):
            return rows_idx[i]
    return -1


def get_element(response):
    for id in response:
        cur = response[id]
        res = {}
        res['row_idx'] = determine_place(cur['name'])

        if 'spent' in cur:
            res['Расход'] = cur['spent']
        if 'impressions' in cur:
            res['Показы'] = cur['impressions']
        if 'click' in cur:
            res['Клики'] = cur['clicks']
        if 'join_rate' in cur:
            res['Вступления'] = cur['join_rate']

        yield res


async def print_data(data, day_start, day_finish, page):
    for idx in data:
        for value in data[idx]:
            drange = pygsheets.DataRange(
                    start=(idx + indexes_diff[value], 3 + day_start),
                    end=(idx + indexes_diff[value], 3 + day_finish),
                    worksheet=page
            )
            drange.update_values([data[idx][value]])


async def fill_page(account, client, page, new=False):
    last = datetime.now().day
    print(f'Filling {client} {new}')

    nameCell = pygsheets.Cell((0, 0), worksheet=page)
    nameCell.set_value(client['name'])
    page.resize(cols=60)
    
    if new:
        data = {rows_idx[i]: {item: [0 for _ in range(1, last)] for item in list_items} for i in rows_idx}
        for day in range(1, last): 
            result = await parse_campaigns(account, client['id'], day)
            for element in get_element(result):
                if element['row_idx'] != -1:
                    for value in list_items:
                        if value in element:
                            try:
                                data[element['row_idx']][value][day - 1] += float(element[value])
                            except IndexError as e:
                                print(f'Error: {e}')
            sleep(4)
        await print_data(data, 1, last - 1, page)
        sleep(4)

    data = {rows_idx[i]: {item: [0] for item in list_items} for i in rows_idx}
    result = await parse_campaigns(account, client['id'], last)
    for element in get_element(result):
        if element['row_idx'] != -1:
            for value in list_items:
                if value in element:
                    try:
                        data[element['row_idx']][value][0] += float(element[value])
                    except IndexError as e:
                        print(f'Error: {e}')

    await print_data(data, last, last, page) 
    sleep(4)


async def full_sync_with_docs():
    accounts = parse_accounts()
    for account in accounts:

        clients = get_clients(account)
        for client in clients:

            new = False
            try:
                current_page = report.worksheet_by_title(str(client['name']))
            except pygsheets.exceptions.WorksheetNotFound:
                new = True
                template = report.worksheet_by_title('Шаблон')
                current_page = report.add_worksheet(str(client['name']), cols=60, src_worksheet=template)

            await fill_page(account, client, current_page, new)

        sleep(5)


async def sync_func():
    print('Запускается цикл')
    while True:
        now = datetime.now()

        if now.time() > time(21):
            next_date = now + timedelta(days=1)
        else:
            next_date = now
        delta = (datetime.fromisoformat(f'{next_date.date()} {time(20)}') - now).seconds

#        await full_sync_with_docs()

        print(f'Synchronized. Next sync in {delta} s')

        await asyncio.sleep(delta)
