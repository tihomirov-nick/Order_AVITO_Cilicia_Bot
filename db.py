import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('menu.db')
    cur = base.cursor()


async def get_cat_buttons(cat_name):
    return cur.execute("SELECT item_data FROM UNDER_MENU WHERE cat_name == ?", (cat_name,)).fetchall()[0]


async def get_menu_buttons(menu):
    return str(cur.execute("SELECT items FROM MENU WHERE types == ?", (menu,)).fetchall()[0][0]).split("\n")


async def get_all_menu():
    return cur.execute("SELECT * FROM BIG_MENU").fetchall()


async def get_photo(cat_name):
    return cur.execute("SELECT photo_id FROM UNDER_MENU WHERE cat_name == ?", (cat_name,)).fetchall()[0][0]


# Order

async def check_order_status(id):
    user_order = cur.execute("SELECT * FROM USER_ORDER WHERE user_id == ?", (id,)).fetchall()

    total_price = 0
    for i in user_order:
        total_price += int(str(i[2]).replace("\r", ""))

    return total_price


async def delete_item_from_order(id, name):
    cur.execute("DELETE FROM USER_ORDER WHERE user_id == ? and item_name == ?", (id, name,))
    base.commit()


async def add_to_order(user_id, name, price):
    cur.execute("INSERT INTO USER_ORDER VALUES (?, ?, ?)", (user_id, name, price,))
    base.commit()


async def get_all_prices(id):
    user_order = cur.execute("SELECT * FROM USER_ORDER WHERE user_id == ?", (id,)).fetchall()

    all_prices = []

    for i in user_order:
        all_prices.append(i[2])

    return all_prices


async def get_all_dishes(id):
    user_order = cur.execute("SELECT * FROM USER_ORDER WHERE user_id == ?", (id,)).fetchall()

    all_dishes = []

    for i in user_order:
        all_dishes.append(i[1])

    return all_dishes


# Pay

async def get_all_order(id):
    return cur.execute("SELECT * FROM USER_ORDER WHERE user_id == ?", (id,)).fetchall()


async def add_new_pay(user_id, order, bill_id):
    cur.execute("INSERT INTO reciep VALUES (?, ?, ?)", (user_id, order, bill_id,))
    base.commit()


async def get_new_pay(bill_id):
    result = cur.execute("SELECT * FROM reciep WHERE bill_id == ?", (bill_id,)).fetchmany(1)
    if not bool(len(result)):
        return False
    else:
        return result[0]


async def delete_new_pay(bill_id):
    cur.execute("DELETE FROM reciep WHERE bill_id == ?", (bill_id,))
    base.commit()


async def get_order_text(bill_id):
    pay = cur.execute("SELECT * FROM reciep WHERE bill_id == ?", (bill_id,)).fetchone()
    return pay[1]