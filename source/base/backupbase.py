import json
from source.base.base import *
from source.base.userbase import *
from source.parser import *
from datetime import datetime
from calendar import monthrange

# CREATE TABLE `backup` (
#                     `id` bigint NOT NULL PRIMARY KEY,
#                     `today` nvarchar(3000) DEFAULT "[]",
#                     `yesterday` nvarchar(3000) DEFAULT "[]",
#                     `week` nvarchar(3000) DEFAULT "[]",
#                     `2week` nvarchar(3000) DEFAULT "[]",
#                     `month` nvarchar(3000) DEFAULT "[]"
#                 );
#                 """

time_periods = ['today', 'yesterday', 'week', '2week', 'month']


def backup_get(id, period):
    sql = f"SELECT {period} FROM backup WHERE id = %s"
    res = fetchone_execute(sql, (id, ))[period]
    return json.loads(res)

def backup_set(id, period, data):
    info = backup_get(id, period)
    tmp = info[0]
    info[0] = data

    now = datetime.now()
    if now.hour == 0:
        if (period == 'today' or period == 'yesterday') or \
           (now.weekday() == 6 and period == 'week') or \
           (now.weekday() == 6 and now.isocalendar().week % 2 == 0 and period == '2week') or \
           (now.day == monthrange(now.year, now.month)[1] and period == 'month'):
            info[1] = tmp

    update(id, period, json.dumps(info), 'backup')


async def backup_sync():
    for user in users_get_clients():
        cur_settings = users_get_company(user['id'])
        for account_id in cur_settings:
            for client_id in cur_settings[account_id]:
                for period in time_periods:
                    data = await campaigns_data_addition(int(account_id), int(client_id), period)
                    backup_set(user['id'], period, data)


async def sync_backup_func():
    print('Запускается backup')
    while True:
        await backup_sync()

        await asyncio.sleep(3600)

