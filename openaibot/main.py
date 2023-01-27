from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from my_sources import botTOKEN, text_davinci003

# Initialize bot and dispatcher
bot = Bot(token=botTOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class Question(StatesGroup):
    question = State()  # Will be represented in storage as 'Question:question'


@dp.message_handler(commands='ask')
async def start(message: types.Message):
    await Question.question.set()  # Set conversation
    await message.reply(f"<b>{message.from_user.first_name}</b>,\n🫵 send your question...",
                        parse_mode='HTML')


# Get a response and pass the user's question to the GPT-3 (Text-Davinci-003)
@dp.message_handler(state=Question.question)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_question = data['text']
        await message.answer_chat_action("typing")
        await message.reply(f"<b>Text-Davinci-003:</b>\n{text_davinci003(user_question=user_question)}",
                            parse_mode='HTML')
    # Finish conversation
    await state.finish()


@dp.message_handler(commands='start')
async def start(message: types.Message):
    await message.reply("<strong>Hi!</strong>👋\n"
                        "<i><b>Text-Davinci-003</b></i> <i>is the capable model, designed specifically for instruction-following tasks</i>.\n"
                        "<i>This enables it to respond concisely and accurately without the need for any examples given in the prompt</i>.🧐\n"
                        "<i>If you want to ask him a question, type</i> <b>/ask</b>",
                        parse_mode='HTML')


@dp.message_handler()
async def echo(message: types.Message):
    await message.reply("<strong>Hi!</strong>👋\n"
                        "<b>Don't torture the bot, just type /start or /ask </b>😜",
                        parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
