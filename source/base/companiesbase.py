from source.base.base import *
from source.parser import *
from source.texts import *


def accounts_sync():
    res = pre_parse_accounts()
    drop_accounts_query = 'DROP TABLE IF EXISTS `accounts`'
    create_accounts_query = """
            CREATE TABLE `accounts` (
                `account_id` bigint NOT NULL PRIMARY KEY,
                `account_name` nvarchar(200),
                `account_status` int
            );
            """
    commit_execute(drop_accounts_query)
    commit_execute(create_accounts_query)

    for account_id in res:
        sql = f'INSERT INTO accounts (account_id) VALUES (%s)'
        commit_execute(sql, (account_id))
        for field in res[account_id]:
            sql = f'UPDATE accounts SET {field} = %s WHERE account_id = %s'
            commit_execute(sql, (res[account_id][field], account_id))

    print('accounts sync success')



def clients_sync():
    drop_clients_query = 'DROP TABLE IF EXISTS `clients`'
    create_clients_query = """
            CREATE TABLE `clients` (
                `id` bigint NOT NULL PRIMARY KEY,
                `name` nvarchar(200),
                `day_limit` nvarchar(50),
                `all_limit` nvarchar(50),
                `account_id` bigint
            );
            """
    commit_execute(drop_clients_query)
    commit_execute(create_clients_query)

    for accountId in parse_accounts():
        res = pre_get_clients(accountId)

        for data in res:
            sql = f'INSERT INTO clients (id, account_id) VALUES (%s, %s)'
            commit_execute(sql, (data['id'], accountId))
            for field in data:
                sql = f'UPDATE clients SET {field} = %s WHERE id = %s'
                commit_execute(sql, (data[field], data['id']))

    print('clients sync success')



def client_get_stats(account_id, client_id, time):
    result = parse_clients(account_id, client_id, time)

    for id in result:
        txt = ''

        for line in stats_template.split('\n'):
            cur_line = ''
            for word in line.split():
                if word[0] != "'":
                    cur_line += word
                else:
                    word = word[1:]
                    if word in result[id]:
                        cur_line += str(result[id][word])
                    else:
                        cur_line += '-'

                cur_line += ' '
            cur_line += '\n'

            txt += cur_line

        return txt


def clients_get_list(accountId):
    result = get_clients(accountId)
    txt = f'AccountId: `{accountId}`\n\n'
    for item in result:

        name = item["name"]
        if name in clients_rename_dict:
            name = clients_rename_dict[name]

        txt += f'ID: `{item["id"]}`, название: {name}\n\n'
    return txt


def accounts_get_list():
    result = parse_accounts()
    accounts = []
    txt = ''
    for id in result:
        accounts.append(id)

        name = result[id]["account_name"]
        if name in accounts_rename_dict:
            name = accounts_rename_dict[name]

        txt += f'ID: `{result[id]["account_id"]}`, название: {name}, ' \
               f'статус: {"✅" if result[id]["account_status"] else "❌"}\n\n'
    return txt, accounts


accounts_sync()
clients_sync()
