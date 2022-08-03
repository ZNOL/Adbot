import asyncio
import requests
import json
from config import *
from pprint import pprint
from datetime import datetime, timedelta
from time import sleep
from source.texts import *
from source.base.base import *


def get_time(time):
    match time:
        case 'overall':
            return 'overall', 0, 0
        case 'today':
            return 'day', datetime.now().date(), datetime.now().date()
        case 'yesterday':
            x = (datetime.now() - timedelta(days=1)).date()
            return 'day', x, x
        case 'week':
            x = (datetime.now() - timedelta(weeks=1)).date()
            return 'week', x, x
        case '2week':
            x = (datetime.now() - timedelta(weeks=1)).date()
            return 'week', x, datetime.now().date()
        case 'month':
            x = (datetime.now() - timedelta(weeks=4, days=3)).strftime('%Y-%m')
            return 'month', x, x
        case _:
            diff_days = datetime.now().day - int(time)
            x = (datetime.now() - timedelta(days=int(diff_days))).date()
            return 'day', x, x


def pre_parse_accounts():
    url = f'https://api.vk.com/method/ads.getAccounts?v=5.131&access_token={ACCESS_TOKEN}'
    response = requests.get(url)
    response = json.loads(response.text)
    res = {}

    try:
        for item in response['response']:
            name = item['account_name']
            if name in accounts_rename_dict:
                name = accounts_rename_dict[name]

            res[item['account_id']] = {
                'account_id': item['account_id'],
                'account_name': name,
                'account_status': item['account_status'],
            }

        return res
    except Exception as e:
        sleep(5)
        return pre_parse_accounts()


def pre_get_clients(account_id):
    url = f'https://api.vk.com/method/ads.getClients?v=5.131&account_id={account_id}&access_token={ACCESS_TOKEN}'
    try:
        response = requests.get(url)
        response = json.loads(response.text)
        clients = response['response']

        for client in clients:
            if client['name'] in clients_rename_dict:
                client['name'] = clients_rename_dict[client['name']]

        return clients
    except KeyError:
        sleep(5)
        return pre_get_clients(account_id)


def parse_accounts():
    sql = 'SELECT * FROM accounts'
    res = fetchall_execute(sql)

    new_res = {}
    for data in res:
        new_res[data['account_id']] = data

    return new_res


def get_clients(account_id):
    sql = 'SELECT * FROM clients WHERE account_id = %s'
    res = fetchall_execute(sql, (account_id, ))

    return res


def parse_clients(account_id, client_id, time='overall'):
    period, date_from, date_to = get_time(time)
    res = {}

    url = f'https://api.vk.com/method/ads.getStatistics?v=5.131&account_id={account_id}' \
          f'&ids_type=client&access_token={ACCESS_TOKEN}&period={period}&date_from={date_from}&date_to={date_to}' \
          f'&ids={client_id}'

    res[client_id] = {'id': client_id}
    try:
        for client in get_clients(account_id):
            if client['id'] == client_id:
                res[client_id].update({field: client[field] for field in client})
                if res[client_id]['name'] in clients_rename_dict:
                    res[client_id]['name'] = clients_rename_dict[res[client_id]['name']]

        response = requests.get(url)
        response = json.loads(response.text)

        for item in response['response']:
            if len(item['stats']):
                res[client_id].update(item['stats'][0])

        return res
    except KeyError as e:
        print(f'KeyError {e}')
        sleep(10)
        return parse_clients(account_id, client_id, time)


async def parse_campaigns(account_id, client_id, time='overall'):
    period, date_from, date_to = get_time(time)

    while True:
        try:
            url = f'https://api.vk.com/method/ads.getCampaigns?v=5.131&account_id={account_id}&access_token={ACCESS_TOKEN}&client_id={client_id}'
            response = requests.get(url)
            response = json.loads(response.text)
            if 'response' not in response:
                raise KeyError
            break
        except KeyError:
            sleep(10)

    res = {}

    await asyncio.sleep(2)

    url = f'https://api.vk.com/method/ads.getStatistics?v=5.131&account_id={account_id}' \
          f'&ids_type=campaign&access_token={ACCESS_TOKEN}&period={period}&date_from={date_from}&date_to={date_to}&ids='

    main_url = url
    ids = []

    for item in response['response']:
        url += f'{item["id"]},'
        ids.append(str(item["id"]))
        res[item['id']] = {'name': item['name'],
                           'type': item['type'],
                           'status': item['status'],
                           'day_limit': item['day_limit'],
                           'all_limit': item['all_limit']}
    url = url[:-1]

    while True:
        try:
            response = requests.get(url)
            response = json.loads(response.text)

            for item in response['response']:
                if 'stats' in item and item['stats']:
                    res[item['id']].update(item['stats'][0])

            return res
        except KeyError as e:  # KeyError
            print(f'KeyError {e}')
            sleep(10)
        except json.decoder.JSONDecodeError:
            for i in range(0, len(ids), 30):
                url = main_url
                url += ','.join(ids[i:i+30])

                while True:
                    response = requests.get(url)
                    response = json.loads(response.text)
                    try:
                        for item in response['response']:
                            if 'stats' in item and item['stats']:
                                res[item['id']].update(item['stats'][0])

                        break
                    except KeyError as e:
                        print(f'KeyError {e} in json.decoder')
                        sleep(10)
                sleep(3)
            return res


async def campaigns_data_addition(account_id, client_id, time='overall'):
    res = {}
    tmp = await parse_campaigns(account_id, client_id, time)

    for id in tmp:
        for field in statistics_fields:
            if field in tmp[id]:
                if field not in res:
                    res[field] = 0

                res[field] += float(tmp[id][field])

    return res



# print(parse_clients(1900013867))

# f = open('result.txt', 'w')
# for client in get_clients():
#     print(client, file=f)
#     newtable = parse_campaigns(str(client['id']), 'today')
#     pprint(newtable, stream=f)
#     print('===========================================', file=f)

# date = (datetime.now() - timedelta(weeks=1)).date()
# newtable = parse_campaigns('month')

# f = open('result.txt', 'w')
# print(parse_campaigns(1900014205, 1606564410))

# for i in range(30):
#     print(parse_campaigns(1900014205, 1606564410, i))
#     sleep(10)
#     print('+' * 30)

# f.close()vim
