from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import random

from pyqiwip2p import QiwiP2P

import db
from create_bot import bot

pay = QiwiP2P(auth_key="eyJ2ZXJzaW9uIjoiUDJQIiwiZGF0YSI6eyJwYXlpbl9tZXJjaGFudF9zaXRlX3VpZCI6Ijc4OGQ1ay0wMCIsInVzZXJfaWQiOiI3OTExNzM0MTgwNyIsInNlY3JldCI6ImRhNThlMTRjZDY2Y2U0NDlmNDQyMDVkYmRkMjUyNTJjMWFkZTVlNjNjZmI5ODlkOTQ5Y2IwN2FmM2JhMGQ3OWUifX0=")


# Home

async def command_start(message: types.Message, state: FSMContext):
    await state.finish()
    total_price = await db.check_order_status(message.from_user.id)
    main_kb = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
        .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))
    await bot.send_message(message.from_user.id, text="Привет", reply_markup=main_kb)


async def cal_command_start(callback: types.CallbackQuery, state: FSMContext):
    await state.finish()
    total_price = await db.check_order_status(callback.message.chat.id)
    main_kb = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
        .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))
    await callback.message.edit_text(text="Привет", reply_markup=main_kb)


# Menu

async def main_menu(callback: types.CallbackQuery):
    all_buttons = await db.get_all_menu()

    all_menu = InlineKeyboardMarkup()
    for button in all_buttons:
        all_menu.add(InlineKeyboardButton(text=str(button[0]), callback_data="OPEN_MENU/" + str(button[0]) + "/0"))  # command + name_of_category + page_num
    all_menu.add(InlineKeyboardButton(text="←", callback_data="HOME"))

    await callback.message.edit_text(text="Выберите меню", reply_markup=all_menu)


async def menu(callback: types.CallbackQuery):
    data = callback.data.replace("OPEN_", "").split("/")

    all_cats_kb = InlineKeyboardMarkup()

    all_buttons = await db.get_menu_buttons(data[1])

    for dish in all_buttons:
        all_cats_kb.add(InlineKeyboardButton(text=str(dish).replace("\r", ""), callback_data="OPEN_CAT" + str(dish).replace("\r", "")))

    all_cats_kb.add(InlineKeyboardButton(text="←", callback_data="HOME"))

    await callback.message.edit_text(text="Выберите категорию", reply_markup=all_cats_kb)


async def cats(callback: types.CallbackQuery):
    cat_name = callback.data.replace("OPEN_CAT", "")
    all_dishes = str((await db.get_cat_buttons(cat_name))[0]).split("\r\n")
    photo_id = await db.get_photo(cat_name)

    cat_kb = InlineKeyboardMarkup()
    for dish in all_dishes:
        cat_kb.add(InlineKeyboardButton(text=dish, callback_data="buy" + dish))

    await callback.message.delete()
    print(photo_id)
    await callback.bot.send_photo(chat_id=callback.message.chat.id, photo=photo_id, caption="Выберите позицию для добавления в заказ", reply_markup=cat_kb)

    # file_id = (await db.get_photo_id(page, menu))[0]
    #
    # await callback.message.delete()
    # await callback.bot.send_photo(callback.message.chat.id, photo=file_id, caption=name, reply_markup=all_dishes)


# Order

async def add_to_order(callback: types.CallbackQuery):
    data = (callback.data.replace("buy", "")).split(" - ")
    name = data[0]
    price = data[1]
    await db.add_to_order(callback.message.chat.id, name, price)

    total_price = await db.check_order_status(callback.message.chat.id)
    main_kb = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
        .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))

    await callback.message.delete()
    await callback.bot.send_message(callback.message.chat.id, text=f'''Позиция "{name}" добавлена в заказ''', reply_markup=main_kb)


async def order(callback: types.CallbackQuery):
    all_dishes = await db.get_all_dishes(callback.message.chat.id)
    all_prices = await db.get_all_prices(callback.message.chat.id)

    if len(all_dishes) != 0:
        order_kb = InlineKeyboardMarkup()
        for i in range(len(all_dishes)):
            order_kb.add(InlineKeyboardButton(text=all_dishes[i] + " - " + all_prices[i] + " руб.", callback_data="delete_item/" + all_dishes[i]))
        order_kb.add(InlineKeyboardButton(text="←", callback_data="HOME"), InlineKeyboardButton(text="Оформить", callback_data="Оформить"))

        await callback.message.edit_text(text=f"Ваш заказ на сумму {await db.check_order_status(callback.message.chat.id)} руб.\n\nНажмите на позицию, чтобы удалить ее из заказа", reply_markup=order_kb)
    else:
        total_price = await db.check_order_status(callback.message.chat.id)
        main_kb = InlineKeyboardMarkup() \
            .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
            .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))

        await callback.message.edit_text(text=f'''Ваш заказ пуст''', reply_markup=main_kb)


async def delete_item_from_order(callback: types.CallbackQuery):
    item_name = callback.data.replace("delete_item/", "")
    await db.delete_item_from_order(callback.message.chat.id, item_name)

    all_dishes = await db.get_all_dishes(callback.message.chat.id)
    all_prices = await db.get_all_prices(callback.message.chat.id)

    if len(all_dishes) != 0:
        order_kb = InlineKeyboardMarkup()
        for i in range(len(all_dishes)):
            order_kb.add(InlineKeyboardButton(text=all_dishes[i] + " - " + all_prices[i] + " руб.", callback_data="delete_item/" + all_dishes[i]))
        order_kb.add(InlineKeyboardButton(text="←", callback_data="HOME"), InlineKeyboardButton(text="Оформить", callback_data="Оформить"))

        await callback.message.edit_text(text=f'''Позиция "{item_name}" успешно удалена''', reply_markup=order_kb)
    else:
        total_price = await db.check_order_status(callback.message.chat.id)
        main_kb = InlineKeyboardMarkup() \
            .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
            .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))
        await callback.message.edit_text(text=f'''Позиция "{item_name}" успешно удалена''', reply_markup=main_kb)


# Booking

class Book(StatesGroup):
    name = State()
    count = State()
    num = State()


async def booking_1(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Введите на чье имя будет произведено бронирование")
    await Book.name.set()


async def booking_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await bot.send_message(message.from_user.id, text="Введите количество гостей")
    await Book.count.set()


async def booking_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['count'] = message.text
    await bot.send_message(message.from_user.id, "Введите ваш контактный номер телефона")
    await Book.num.set()


async def booking_4(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['num'] = message.text
        await bot.send_message(message.from_user.id, text=data['name'] + data['count'] + data['num'])
    total_price = await db.check_order_status(message.from_user.id)
    main_kb = InlineKeyboardMarkup() \
        .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
        .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))
    await bot.send_message(message.from_user.id, text="Ожидайте, с вами свяжутся для уточнения деталей", reply_markup=main_kb)
    await state.finish()


# Pay

class MakePay(StatesGroup):
    phone = State()


async def pay_1(callback: types.CallbackQuery):
    await callback.message.edit_text(text="Введите ваш номер телефона")
    await MakePay.phone.set()


async def pay_2(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
        order = f"Заказ на номер: {data['phone']}\n"

    id = message.from_user.id
    total_price = await db.check_order_status(id)
    all_dishes = await db.get_all_order(id)
    comment = f'''{id}_{random.randint(10000, 99999)}'''
    bill = pay.bill(amount=total_price, lifetime=15, comment=comment)

    for pos in all_dishes:
        order = order + str(pos[1]) + " - " + str(pos[2]) + "\n"

    await db.add_new_pay(id, order, bill.bill_id)

    await bot.send_message(message.from_user.id, text="Вы можете оплатить заказ через Qiwi по ссылке ниже", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Qiwi", url=bill.pay_url)).add(InlineKeyboardButton(text="Проверить платёж", callback_data="check_pay" + str(bill.bill_id))))
    await state.finish()


async def pay_3(callback: types.CallbackQuery):
    bill_id = callback.data.replace("check_pay", "")
    info = await db.get_new_pay(bill_id)

    if info:
        if str(pay.check(bill_id=bill_id).status) == "PAID":
            order_text = await db.get_order_text(bill_id)
            total_price = await db.check_order_status(callback.message.chat.id)
            main_kb = InlineKeyboardMarkup() \
                .add(InlineKeyboardButton(text="Меню", callback_data="Меню"), InlineKeyboardButton(text="Бронирование", callback_data="Бронирование")) \
                .add(InlineKeyboardButton(text="Контакты", callback_data="Контакты"), InlineKeyboardButton(text=f"Заказ {total_price} руб.", callback_data="Корзина"))
            await bot.send_message(callback.message.chat.id, text=order_text, reply_markup=main_kb)
            await db.delete_new_pay(bill_id)
        else:
            await callback.message.edit_text(text="Счет не оплачен", reply_markup=InlineKeyboardMarkup().add(InlineKeyboardButton(text="Проверить платёж", callback_data="check_pay" + str(bill_id))))
    else:
        await callback.message.edit_text(text="Счет на оплату не найден")


# Contacts

async def contacts(callback: types.CallbackQuery):
    contact_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text="VK", url="https://vk.com/resto.cilicia"), InlineKeyboardButton(text="Inst", url="https://instagram.com/resto_cilicia?igshid=YmMyMTA2M2Y=")).add(InlineKeyboardButton(text="←", callback_data="HOME"))

    await callback.message.edit_text(text='''Ресторан армянской кухни «Киликия» 😍
📍 Грибоедова, 40 | Гороховая, 26 
📞 88123272208 
🎙 Живая музыка пт|сб 20:00-23:00
🛵 Доставка 11:00 - 04:30''', reply_markup=contact_kb)


async def get_photo_id(message: types.Message):
    file_id = message.photo[0].file_id
    await bot.send_message(message.from_user.id, text=file_id)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start'], state='*')
    dp.register_callback_query_handler(cal_command_start, lambda c: c.data == "HOME")

    dp.register_callback_query_handler(main_menu, lambda c: c.data == "Меню")
    dp.register_callback_query_handler(menu, lambda c: c.data and c.data.startswith("OPEN_MENU"))
    dp.register_callback_query_handler(cats, lambda c: c.data and c.data.startswith("OPEN_CAT"))

    dp.register_callback_query_handler(add_to_order, lambda c: c.data and c.data.startswith("buy"))
    dp.register_callback_query_handler(delete_item_from_order, lambda c: c.data and c.data.startswith("delete_item/"))
    dp.register_callback_query_handler(order, lambda c: c.data == "Корзина")

    dp.register_callback_query_handler(pay_1, lambda c: c.data == "Оформить")
    dp.register_message_handler(pay_2, state=MakePay.phone)
    dp.register_callback_query_handler(pay_3, lambda c: c.data and c.data.startswith("check_pay"))

    dp.register_callback_query_handler(booking_1, lambda c: c.data == "Бронирование")
    dp.register_message_handler(booking_2, state=Book.name)
    dp.register_message_handler(booking_3, state=Book.count)
    dp.register_message_handler(booking_4, state=Book.num)

    dp.register_callback_query_handler(contacts, lambda c: c.data == "Контакты")

    dp.register_message_handler(get_photo_id, content_types=['photo'])
