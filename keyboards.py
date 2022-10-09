from sqlite import SQLighter

dbase = SQLighter('db.db')


from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

button_reg = KeyboardButton("Зарегестрироваться📝")

button_wallet = KeyboardButton('Кошелек 👛')

button_customer = KeyboardButton('Сделать заказ 🙋🏼‍♂')
button_executor = KeyboardButton('Найти заказ 👨‍🏫')
button_technical_support = KeyboardButton('Техническая поддержка 👨‍🔧')
button_personal_area = KeyboardButton('Личный кабинет 🧰')
button_rules = KeyboardButton('Правила 📚')
button_home = KeyboardButton('Главное меню 🏠')

button_balance = KeyboardButton('Баланс 💰')

button_confirm = KeyboardButton('Подтвердить ✅')
button_undo = KeyboardButton('Отменить ❌')

button_replenishment = KeyboardButton('Пополнить 💸')
button_withdrawal_of_funds = KeyboardButton('Вывести 🏧')

start_menu = ReplyKeyboardMarkup().add(button_wallet, button_customer, button_executor, button_personal_area, button_rules,
                                       button_technical_support)

wallet_menu = ReplyKeyboardMarkup().add(button_balance, button_replenishment,
                                        button_withdrawal_of_funds, button_home)

replenishment_menu = ReplyKeyboardMarkup().add(button_confirm, button_undo)

home_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_home)

reg_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(button_reg)

place_menu = ReplyKeyboardMarkup()
place = dbase.selectPlace()
for places in place:
    for p in places:
        place_menu.add(
            f'{p}'
        )

domain_menu_s = ReplyKeyboardMarkup()
domain_menu_u = ReplyKeyboardMarkup()

for domains in dbase.selectDomains('Школа'):
    for d in domains:
        domain_menu_s.add(
            f'{d}'
        )
for domains in dbase.selectDomains('Университет'):
    for d in domains:
        domain_menu_u.add(
            f'{d}'
        )

button_next = KeyboardButton('Вперед ➡')
button_undo = KeyboardButton('Назад ⬅')
next_menu = ReplyKeyboardMarkup().add(button_next).add(button_undo)
