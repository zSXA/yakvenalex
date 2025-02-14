from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message
from keyboards.all_keyboards import main_kb, create_spec_kb, create_rat
from keyboards.inline_kbs import ease_link_kb, get_inline_kb, create_qst_inline_kb
from utils.utils import get_random_person
from aiogram.types import CallbackQuery
from create_bot import questions, admins
import asyncio
from aiogram.utils.chat_action import ChatActionSender
from create_bot import questions, bot
from filters.IsAdmin import IsAdmin
import pytz

start_router = Router()

@start_router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):

    command_args: str = command.args if command is not None else None
    if command_args:
        await message.answer(
            f'Запуск сообщения по команде /start используя фильтр CommandStart() c меткой <b>{command_args}</b>',
            reply_markup=main_kb(message.from_user.id))
    else:
        await message.answer(
            f'Запуск сообщения по команде /start используя фильтр CommandStart() без метки',
            reply_markup=main_kb(message.from_user.id))

@start_router.message(Command(commands=['settings', 'about']))
async def univers_cmd_handler(message: Message, command: CommandObject):
    command_args: str = command.args
    command_name = 'settings' if 'settings' in message.text else 'about'
    response = f'Была вызвана команда /{command_args}'
    if command_args:
        response += f' с меткой <b>{command_args}</b>'
    else:
        response += ' без метки'
    await message.answer(response)

@start_router.message(Command('start_2'))
async def cmd_start_2(message: Message):
    await message.answer('Запуск сообщения по команде /start_2 используя фильтр Command()', reply_markup=create_spec_kb())

@start_router.message(F.text == '/start_3')
async def cmd_start_3(message: Message):
    await message.answer('Запуск сообщения по команде /start_3 используя магический фильтр F.text', reply_markup=create_rat())

@start_router.message(F.text == 'Давай инлайн!')
async def get_inline_btn_link(message: Message):
    await message.answer('Вот тебе инлайн клавиатура со ссылками!', reply_markup=ease_link_kb())
    await message.answer('Вот тебе инлайн клавиатура с CallbackQuery', reply_markup=get_inline_kb())

@start_router.callback_query(F.data == 'get_person')
async def send_random_person(call: CallbackQuery):
    await call.answer('Генерирую случайного пользователя', show_alert=True)
    user = get_random_person()
    formatted_message = (
        f"👤 <b>Имя:</b> {user['name']}\n"
        f"🏠 <b>Адрес:</b> {user['address']}\n"
        f"📧 <b>Email:</b> {user['email']}\n"
        f"📞 <b>Телефон:</b> {user['phone_number']}\n"
        f"🎂 <b>Дата рождения:</b> {user['birth_date']}\n"
        f"🏢 <b>Компания:</b> {user['company']}\n"
        f"💼 <b>Должность:</b> {user['job']}\n"
    )
    await call.message.answer(formatted_message)


@start_router.callback_query(F.data == 'back_home')
async def go_back_home(call: CallbackQuery):
    await call.answer('На главную ...', show_alert=False)
    await call.message.answer('Главное меню', reply_markup=main_kb(call.message.from_user.id))

@start_router.message(Command('faq'))
async def cmd_start_2(message: Message):
    await message.answer('Сообщение с инлайн клавиатурой с вопросами', reply_markup=create_qst_inline_kb(questions))

@start_router.callback_query(F.data.startswith('qst_'))
async def cmd_start(call: CallbackQuery):
    await call.answer()
    qst_id = int(call.data.replace('qst_', ''))
    qst_data = questions[qst_id]
    msg_text = f'Ответ на вопрос {qst_data.get("qst")}\n\n' \
               f'<b>{qst_data.get("answer")}</b>\n\n' \
               f'Выберите другой вопрос:'
    async with ChatActionSender(bot=bot, chat_id=call.from_user.id, action="typing"):
        await asyncio.sleep(2)
        await call.message.answer(msg_text, reply_markup=create_qst_inline_kb(questions))

@start_router.message(F.text.lower().contains('подписывайся'))
async def process_find_word(message: Message):
    await message.answer('В твоем сообщении было найдено слово "подписывайся", а у нас такое писать запрещено!')

@start_router.message(F.text.regexp(r'(?i)^Привет, .+'))
async def process_find_reg(message: Message):
    await message.answer('И тебе здарова! Че нада?')

@start_router.message(F.text.lower().contains('подписывайся'), IsAdmin(admins))
async def process_find_word(message: Message):
    await message.answer('О, админ, здарова! А тебе можно писать подписывайся.')

@start_router.message(F.text.lower().contains('подписывайся'))
async def process_find_word(message: Message):
    await message.answer('В твоем сообщении было найдено слово "подписывайся", а у нас такое писать запрещено!')



def get_msc_date(utc_time):
    # Задаем московский часовой пояс
    moscow_tz = pytz.timezone('Europe/Moscow')
    # Переводим в московский часовой пояс
    moscow_time = utc_time.astimezone(moscow_tz)
    return moscow_time


@start_router.message(F.text.lower().contains('охотник'))
async def cmd_start(message: Message):
    # Отправка обычного сообщения
    await message.answer('Я думаю, что ты тут про радугу рассказываешь')

    # то же действие, но через объект бота
    await bot.send_message(chat_id=message.from_user.id, text='Для меня это слишком просто')

    # ответ через цитату
    msg = await message.reply('Ну вот что за глупости!?')

    # ответ через цитату, через объект bot
    await bot.send_message(chat_id=message.from_user.id, text='Хотя, это забавно...',
                           reply_to_message_id=msg.message_id)
    
    # переслать сообщение
    await bot.forward_message(chat_id=message.from_user.id, from_chat_id=message.from_user.id, message_id=msg.message_id)

    data_task = {'user_id': message.from_user.id, 'full_name': message.from_user.full_name,
                 'username': message.from_user.username, 'message_id': message.message_id, 'date': get_msc_date(message.date)}
    print(data_task)

