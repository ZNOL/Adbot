from cgitb import reset
import json
from source.base.base import *


def users_add(id, is_controller=0, is_admin=0):
    sql = f"INSERT INTO users (id, is_client, is_admin) VALUES (%s, %s, %s)"
    commit_execute(sql, (id, is_controller, is_admin))


def users_delete(id):
    sql = f"DELETE FROM users WHERE id = %s"
    commit_execute(sql, (id, ))


def users_get(id):
    if str(id).isdigit():
        sql = f"SELECT * FROM users WHERE id = %s"
    else:
        sql = f"SELECT * FROM users WHERE nickname = %s"
    return fetchone_execute(sql, (id, ))


def users_get_all():
    sql = f"SELECT * FROM users"
    return fetchall_execute(sql)


def users_is_client(id):
    sql = f"SELECT is_client FROM users WHERE id = %s"
    try:
        return fetchone_execute(sql, (id, ))["is_client"]
    except TypeError:
        return 0


def users_is_admin(id):
    sql = f"SELECT is_admin FROM users WHERE id = %s"
    try:
        return fetchone_execute(sql, (id, ))["is_admin"]
    except TypeError:
        return 0


def users_get_admins():
    sql = f"SELECT id FROM users WHERE is_admin = 1"
    return fetchall_execute(sql)

def users_get_clients():
    sql = f"SELECT * FROM users WHERE is_client = 1"
    return fetchall_execute(sql)


def users_forward_id(id):
    sql = f"SELECT forward_id FROM users WHERE id = %s"
    return fetchone_execute(sql, (id, ))["forward_id"]


def users_get_company(id):
    sql = f'SELECT companies FROM users WHERE id = %s'
    s = fetchone_execute(sql, (id, ))['companies']
    return json.loads(s)


def users_clear_answer(id):
    sql = f'UPDATE users SET answers = %s WHERE id = %s'
    commit_execute(sql, ("", id))


def users_get_answer(id):
    sql = f'SELECT answers FROM users WHERE id = %s'
    result = fetchone_execute(sql, (id, ))['answers']
    if not result:
        result = ''
    return result


def users_add_answer(id, idx):
    txt = users_get_answer(id)
    if not txt:
        txt = ''
    else:
        txt += ','
    update(id, 'answers', txt + f'/{idx}', 'users')
