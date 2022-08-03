from source.base.base import *


def buttons_delete(id, onlyOne=False):
    sql = f"DELETE FROM buttons WHERE id = %s"

    buttonInfo = buttons_get(id=id)
    if buttonInfo["prev_id"] > 0:
        new_count = buttons_get(id=buttonInfo["prev_id"])["next_count"]
        new_count = new_count - 1 if new_count - 1 >= 0 else 0
        update(buttonInfo["prev_id"], 'next_count', new_count, 'buttons')

    if not onlyOne:
        for value in buttons_get_all(id):
            buttons_delete(value["id"])

    commit_execute(sql, (id, ))


def buttons_get(id=None, value=None):
    sql = f"SELECT * FROM buttons WHERE "
    if id is not None:
        sql += "id = %s"
        values = (id, )
    else:
        sql += "value = %s"
        values = (value, )
    return fetchone_execute(sql, values)


def buttons_get_all(prev_id=None):
    sql = f"SELECT * FROM buttons"
    values = None
    if prev_id is not None:
        sql += f" WHERE prev_id = %s"
        values = (prev_id, )
    return fetchall_execute(sql, values)

