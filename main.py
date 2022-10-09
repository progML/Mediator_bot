import re
from datetime import datetime

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import InputMediaPhoto
from aiogram.utils import executor

import keyboards as kb

from config import TOKEN
from payment import payment_history_last, wallet_money, random_comment

from sqlite import SQLighter
from utils import States

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware())

dbase = SQLighter('db.db')

info_main = "Добро пожаловать в главное меню! Вот что у нас тут есть:\n" \
            "\n/wallet - меню кошелька, в котором вы можете проверить свой баланс или пополнить счет.\n" \
            "\n/make_an_order - отправьте ваше задание нашему боту, чтобы наши эксперты помогли решить его вам.\n" \
            "\n/find_order - если вы эксперт, переходите в этот раздел и посмотрите список доступных заданий.\n" \
            "\n/personal_area - личный кабинет, здесь вы можете просматривать, подтверждать выполнение или удалять отправленные вами заказы.\n" \
            "\n/rules - основные правила нашего теллеграм-бота.\n" \
            "\n/technical_support - вам нужна помощь?\n"

info_payment = 'Вы открыли раздел кошелька, здесь вы можете выполнить следующие действия:\n' \
               '\n/balance - узнать баланс вашего счета.\n' \
               '\n/top_up_balance - пополнить баланс.\n' \
               '\n/withdrawal_of_funds - вывести средства с вашего счета.\n' \
               '\n/home - вернуться в главное меню.\n'


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    # если у юзера нет никнейма, просим создать его
    if message.from_user.username is None:
        await message.answer(
            "Не удалось пройти регистрацию, пожалуйста проследуйте инструкции ниже. \n"
            "1) Зайдите в настройки теллеграмма \n"
            "2) Во вклад Аккаунт в поле 'Имя пользователя' выберите любой свободный ник \n"
            "3) Нажмите на кнопку 'Зарегестрироваться'", reply_markup=kb.reg_menu)
        await States.Reg_0.set()


    elif not dbase.get_user(message.from_user.id):
        dbase.add_user(message.from_user.id, message.from_user.username)
        await message.answer(
            info_main,
            reply_markup=kb.start_menu)

        print(message.text[7:])

    else:
        print('Пользователь не создан')
        await message.answer(info_main, reply_markup=kb.start_menu)


@dp.message_handler(state=States.Reg_0)
async def reg_nickname(message: types.Message, state: FSMContext):
    if message.from_user.username is None:
        await message.answer("Никнейм не был задан, проверьти настройки теллеграмма", reply_markup=kb.reg_menu)
    else:
        dbase.add_user(message.from_user.id, message.from_user.username)
        await message.answer(
            info_main,
            reply_markup=kb.start_menu)
        await state.finish()


@dp.message_handler(commands=['help'], state=None)
async def command_info(message: types.Message):
    await message.reply('Допилить')


@dp.message_handler(Text(equals=["Кошелек 👛", "/wallet"]))
async def wallet(message: types.Message):
    if dbase.block_check(message.from_user.id)[0] != "BAN":
        await message.answer(info_payment, reply_markup=kb.wallet_menu)
    else:
        await message.answer("Вас заблокировали, \n"
                             "обратиетсь в тех поддержку: @ProgML для разблакировки.")


@dp.message_handler(Text(equals=["Правила 📚", "/rules"]))
async def rules(message: types.Message):
    await message.reply('У нас нельзя:\n'
                        '1) Спамить\n'
                        '2) Ругаться матом\n'
                        '3) Рекламировать другие ресурсы\n')


@dp.message_handler(Text(equals=["Главное меню 🏠", "/home"]))
async def back_home(message: types.Message):
    await message.answer(info_main, reply_markup=kb.start_menu)


@dp.message_handler(Text(equals=["Пополнить 💸", "/top_up_balance"]))
async def wallet(message: types.Message):
    await message.answer(
        'Пожалуйста, введите номер телефона к которому привязан Qiwi кошелек, и с которого вы будете производить пополнения вашего баланса (Ваши персональные данные не уйдут за пределы бота)\n'
        '\nПример ввода: 9650581883', reply_markup=types.ReplyKeyboardRemove())

    await States.STATE_0.set()


@dp.message_handler(state=States.STATE_0)
async def phone_number(message: types.Message, state: FSMContext):
    phone = message.text
    phone_reg = r'[8-9]{1}[0-9]{9}'
    comment = random_comment()
    if re.match(phone_reg, phone) and len(phone) == 10:
        dbase.get_money(message.from_user.id, phone, comment)
        await message.answer('Ваш счет успешно создан, для его поплнеия вам следует сдеалть следующее:\n'
                             '\n 1. Зайти в приложения QIWI \n'
                             '\n 2. В разделе "Платежи и пеереводы" выбрать пункт: "На QIWI Кошелек" \n'
                             '\n 3. В появившеемся окне вам следует указать номер QIWI: 79313353175 \n'
                             '\n 4. После этого, вам *обязательно* нужно оставить коментарий к платежу,'
                             f' для этого нажмити вкалдку "Коментарий" и укажите слудющий код: {comment}\n'
                             f'\n После оплаты счета, пожалуйста, подтвердите оплату нажав на кнопку: "Подтвердить ✅"',
                             reply_markup=kb.replenishment_menu, parse_mode='Markdown')


    else:
        await message.answer('Ввели номер телефона некоректно, попробуйте еще раз.', reply_markup=kb.wallet_menu)

    await state.finish()


@dp.message_handler(Text(equals=['Подтвердить ✅']))
async def confirm(message: types.Message):
    old_balance = dbase.check_balance(message.from_user.id)[2]
    res = dbase.check(message.from_user.id)
    phoneDB = "+7" + res[1]
    listPayment = payment_history_last()
    for i in range(len(listPayment['data'])):
        if (listPayment['data'][i]['account']) == phoneDB:
            if (listPayment['data'][i]['comment']) == str(res[2]):
                dbase.update_balance(round(listPayment['data'][i]['sum']['amount'] + old_balance, 2),
                                     message.from_user.id)
    dbase.delete_money(message.from_user.id)
    await message.answer('Ваш платеж успешно обработан, проверьте баланс.',
                         reply_markup=kb.wallet_menu)


@dp.message_handler(Text(equals=['Отменить ❌']))
async def undo(message: types.Message):
    dbase.delete_money(message.from_user.id)
    await message.answer('Ваш платеж успешно отменен.', reply_markup=kb.wallet_menu)


@dp.message_handler(Text(equals=['Баланс 💰', '/balance']))
async def balance(message: types.Message):
    await message.answer("На вашем кошельке: " + str(dbase.check_balance(message.from_user.id)[2]) + " рублей",
                         reply_markup=kb.wallet_menu)


@dp.message_handler(Text(equals=['Вывести 🏧', '/withdrawal_of_funds']))
async def send_money(message: types.Message):
    await message.answer("Пожалуйста, введите номер QIWI кошелька, на который мы отправим вам деньги. \n "
                         "\nПример ввода: 9650581883", reply_markup=types.ReplyKeyboardRemove())
    await States.STATE_1.set()


@dp.message_handler(state=States.STATE_1)
async def get_phone(message: types.Message, state=FSMContext):
    try:
        phone = message.text
        phone_reg = r'[8-9]{1}[0-9]{9}'
        balance = dbase.check_balance(message.from_user.id)[2]
        balance_with_commission = balance - (balance * 5) / 100
        if re.match(phone_reg, phone) and len(phone) == 10 and balance_with_commission >= 10:
            await message.answer(
                "Пожалуйста, введите сумму которую вы хотите перевести, обращаем ваше внимание что она не может превышать остаток на вашем кошелке, а также должна"
                "соотвествовать следующим требованиям: \n"
                "\n1. Минимальная сумма для вывода средств 10 рублей\n"
                "\n2. При вводе следует указать только число, например: 340")

            await message.answer(f"\nМаксимальная сумма вывода для вашего кошелька : {balance_with_commission} рублей")
            await state.update_data(phone1=phone, balance=balance_with_commission, balance1=balance)
            await States.next()

        elif balance_with_commission <= 10:
            await message.answer(
                f'Минимальная сумма для вывода средств 10 рублей, на вашем кошельке: {balance_with_commission}',
                reply_markup=kb.wallet_menu)
            await state.finish()
        else:
            await message.answer('Ввели номер телефона некоректно, попробуйте еще раз.', reply_markup=kb.wallet_menu)
            await state.finish()
    except TypeError:
        print("Ошибка в блоке-кода с отправкой денег с бота на кошелек")


@dp.message_handler(state=States.STATE_2)
async def get_amount(message: types.Message, state: FSMContext):
    amount = message.text
    data = await state.get_data()
    phone1 = data.get("phone1")
    balance_with_commission = data.get("balance")
    balance = data.get("balance1")
    try:
        if balance_with_commission >= (float(amount)) >= 10:
            wallet_money("+7" + phone1, amount)
            dbase.update_balance(round(balance - float(amount), 2), message.from_user.id)
            await message.answer('Ваши деньги отправлены к вам на QIWI кошелек.', reply_markup=kb.wallet_menu)
        else:
            await message.answer(
                'Вы превысили остаток на вашем кошельке или ввели сумму меньше минимальной, пожалуйста попробуйте ввести сумму еще раз',
                reply_markup=kb.wallet_menu)
            await state.finish()
    except ValueError:
        await message.answer(f'Вы ввели не корректное значение: {amount}, пример правильного ввода: 200.32',
                             reply_markup=kb.wallet_menu)

    await state.finish()


@dp.message_handler(Text(equals=['Сделать заказ 🙋🏼‍♂', '/make_an_order']))
async def send_work(message: types.Message):
    if dbase.block_check(message.from_user.id)[0] != "BAN":
        balance = dbase.check_balance(message.from_user.id)[2]
        if balance > 0:
            await message.answer('Вы переместились в раздел заказ, выберите категорию для размещения заказа',
                                 reply_markup=kb.place_menu)
            await States.Task_0.set()
        else:
            await message.answer('На вашем балансе нет средств, пополнитесь чтобы создать заказ',
                                 reply_markup=kb.wallet_menu)
    else:
        await message.answer("Вас заблокировали, \n"
                             "обратиетсь в тех поддержку: @ProgML для разблакировки.")


@dp.message_handler(state=States.Task_0)
async def show_domain(message: types.Message, state=None):
    place = message.text
    if place == 'Школа' or place == 'Университет':
        if place == 'Школа':
            await message.answer('Пожалуйста, выберите предмет', reply_markup=kb.domain_menu_s)
        elif place == 'Университет':
            await message.answer('Пожалуйста, выберите предмет', reply_markup=kb.domain_menu_u)
        await States.next()
    else:
        await message.answer('Вы не выбрали учебное заведение, пожалуйста попробуте еще раз...',
                             reply_markup=kb.start_menu)
        await state.finish()


@dp.message_handler(state=States.Task_1)
async def choose_domain(message: types.Message, state: FSMContext):
    s = []
    for domain in dbase.selectAllDomains():
        for dec in domain:
            s.append(dec)
    domain = message.text
    if domain in s:
        async with state.proxy() as data:
            data["domain"] = domain
        await message.answer(
            'Пожалуйста, напишите техническое задание (этот шаг можно пропустить отправив пустое сообщение)',
            reply_markup=types.ReplyKeyboardRemove())
        await States.next()

    else:
        await message.answer('Вы не выбрали ни одного предмета, пожалуйста повторите попытку...',
                             reply_markup=kb.start_menu)
        await state.finish()


@dp.message_handler(state=States.Task_2)
async def set_dz(message: types.Message, state: FSMContext):
    technicalDZ = message.text
    print(technicalDZ)
    async with state.proxy() as data:
        data["technicalDZ"] = technicalDZ
    print(data)
    await message.answer('Отправьте фото вашего задания...')
    await States.next()


@dp.message_handler(state=States.Task_3, content_types=['photo', 'document', 'text'])
async def save_photo(message: types.Message, state: FSMContext):
    if message.photo:
        photo = message.photo[0].file_id
        print(photo)
        async with state.proxy() as data:
            data["photo"] = photo
        await message.answer("Установите крайний срок для выполнения задания,"
                             "пример ввода даты и времени: 22/05/2021 15:40",
                             reply_markup=types.ReplyKeyboardRemove())
        await States.next()
    elif message.document:
        await message.answer("Вы пытаетесь отправить файл, пожалуйста отправьте фото...", reply_markup=kb.start_menu)
        await state.finish()
    elif message.text:
        await message.answer("На данном шаге требовалось отправить фото, попробуйте еще раз...",
                             reply_markup=kb.start_menu)
        await state.finish()
    else:
        await message.answer("Вы пытаетесть отправить больше одного фото...")
        await state.finish()


@dp.message_handler(state=States.Task_4)
async def set_deadline(message: types.Message, state: FSMContext):
    deadline = message.text
    current_datetime = datetime.now()
    try:
        date_str = datetime.strptime(deadline, "%d/%m/%Y %H:%M")
        print(date_str)
        if current_datetime < date_str:
            async with state.proxy() as data:
                data["deadline"] = deadline
            await message.answer(
                "Укажите цену вашего заказа, обращаем ваше внимание, она не может привышать суммы на вашем балансе, пример ввода: 120",
                reply_markup=types.ReplyKeyboardRemove())
            await States.next()
        else:
            await message.answer("Вы должн указать дату которая еще не завершилась, попробуйте еще раз",
                                 reply_markup=kb.start_menu)
            await state.finish()
    except ValueError:
        await message.answer("Вы неправильно указали дату и время, пример правильного формата: 22/05/2021 15:40",
                             reply_markup=kb.start_menu)
        await state.finish()


@dp.message_handler(state=States.Task_5)
async def set_amount(message: types.Message, state: FSMContext):
    amount = message.text
    balance = dbase.check_balance(message.from_user.id)[2]
    try:
        if int(amount) <= balance:
            dbase.update_balance(round(balance - float(amount), 2), message.from_user.id)
            async with state.proxy() as data:
                data["amount"] = amount
            await message.answer("Ваша заявка сформирована, ожидайте когда заказчик найдет вас",
                                 reply_markup=kb.start_menu)
            dbase.addTask(message.from_user.id, data["domain"], data["technicalDZ"], data["photo"], data["deadline"],
                          data["amount"], "waiting")
            print(data["amount"])
            await state.finish()
        else:
            await message.answer(
                "Вы указали сумму заказа превышающию ваш остаток, пополните счет и повторите попытку позже",
                reply_markup=kb.start_menu)
            await state.finish()
    except ValueError:
        await message.answer(f"Вы ввели :{amount}, пример правильного ввода: 120", reply_markup=kb.start_menu)
        await state.finish()


@dp.message_handler(Text(equals=['Найти заказ 👨‍🏫', '/find_order']))
async def find(message: types.Message):
    if dbase.block_check(message.from_user.id)[0] != "BAN":
        await message.answer('Количество заказов \n'
                             f'В университет: {dbase.countPlace("Университет")[0]} \n'
                             f'В школе: {dbase.countPlace("Школа")[0]} \n',
                             reply_markup=kb.place_menu)
        await States.Order_0.set()
    else:
        await message.answer("Вас временно заблокировали, \n"
                             "обратиетсь в тех поддержку: @ProgML для разблакировки.")


@dp.message_handler(state=States.Order_0)
async def show_task_photo(message: types.Message, state=None):
    place = message.text
    result = dbase.selectAllTask(place)
    count = dbase.countPlace(place)
    if len(result) != 0:
        for i in range(count[0]):
            task = [InputMediaPhoto(result[i][3], f"Номер заказа: #{result[i][0]} \n"
                                                  f"Предмет: {result[i][1]} \n"
                                                  f"Дедлайн: {result[i][4]} \n"
                                                  f"Стоимость: {result[i][5]} рублей \n"
                                                  f"Техническое задание: {result[i][2]}")]
            await bot.send_media_group(message.from_user.id, task)
            await state.finish()
        await message.answer("Пожалуйста выберите один из представленных заказов, после чего вы получите контакт"
                             " заказчика для связи с ними.", reply_markup=kb.home_menu)
        await States.Order_1.set()
    else:
        await state.finish()
        await message.answer("На данный момент заказы в данной категории отсутсвуют.", reply_markup=kb.start_menu)


@dp.message_handler(state=States.Order_1)
async def show_contact(message: types.Message, state=None):
    choose = message.text
    username = str(dbase.get_username(choose)[0])
    if message.from_user.username != username:
        await message.answer("Контакт заказчика: @" + username, reply_markup=kb.start_menu)
    else:
        await message.answer("Вы не можете выбрать ваш заказ.", reply_markup=kb.start_menu)
    await state.finish()


@dp.message_handler(Text(equals=["Личный кабинет 🧰", "/personal_area"]))
async def check_local_area(message: types.Message):
    result = dbase.select_task(message.from_user.id)
    count = dbase.count_task(message.from_user.id)
    if len(result) != 0:
        for i in range(count[0]):
            tasks = [InputMediaPhoto(result[i][4], f"Номер заказа: #{result[i][0]} \n"
                                                   f"Дедлайн: {result[i][1]} \n"
                                                   f"Стоимость: {result[i][2]} рублей \n"
                                                   f"Исполнитель : {str(dbase.find_username(result[i][3])[0]) if result[i][3] > -1 else 'еще не найден, ождидайте пока кто-нибудь выберет ваш заказ'}")]
            await bot.send_media_group(message.from_user.id, tasks)


@dp.message_handler(commands=['delete'])
async def delete_command(message: types.Message):
    if dbase.get_admin(message.from_user.id)[0] == 1:
        dbase.delete_task(message.text.split()[1])
        await message.answer("Заказ удален")
    else:
        await message.answer("У вас нет админки...", reply_markup=kb.start_menu)


@dp.message_handler(commands=['ban'])
async def block_delete_command(message: types.Message):
    if dbase.get_admin(message.from_user.id)[0] == 1:
        userId = message.text.split()[1]
        dbase.update_users(dbase.find_userId_taskId(userId))
        dbase.delete_task(userId)
        await message.answer("Неугодный пользователь забанен и сообщение его удалено.")
    else:
        await message.answer("У вас нет админки...", reply_markup=kb.start_menu)


@dp.message_handler(commands=['unban'])
async def block_delete_command(message: types.Message):
    if dbase.get_admin(message.from_user.id)[0] == 1:
        userName = message.text.split()[1]
        print(userName)
        dbase.command_unblock(userName)
        await message.answer("Пользователь разблокирован")
    else:
        await message.answer("У вас нет админки...", reply_markup=kb.start_menu)


@dp.message_handler()
async def other(message: types.Message):
    dbase.delete_money(message.from_user.id)
    await message.answer(
        'Если у вас есть вопросы по работе бота вы можете воспользоваться командой /help или написать в техническую поддержку @ProgML',
        reply_markup=kb.home_menu)


if __name__ == '__main__':
    executor.start_polling(dp)  ##Run
