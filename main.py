from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from pymongo import MongoClient
from config import *
from questions import *
import asyncio

cluster = MongoClient(MongoTOKEN)
db = cluster["Bot"]
quiz = db["Quiz"]

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


kb = InlineKeyboardMarkup(
                              inline_keyboard=[
                                  [
                                      InlineKeyboardButton(
                                          text="Növbəti suala keçid",
                                          callback_data="next_question"
                                      )
                                  ],
                                  [
                                      InlineKeyboardButton(
                                          text="Dayandır",
                                          callback_data="cancel"
                                      )
                                  ]
                              ])

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    for number in range(1, 3):
        mytext = globals()[f'question{number}']
        for num, text in enumerate(mytext[1:4]):
            if text == mytext[-1]:
                correct_index = num
                await message.answer_poll(question=mytext[0],
                                          options=mytext[1:4],
                                          correct_option_id=correct_index,
                                          type='quiz',
                                          is_anonymous=False,
                                          open_period=5,
                                          reply_markup=kb)
                await asyncio.sleep(10)


@dp.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    answer = " ".join(map(str,poll_answer.option_ids))
    quiz.find_one_and_update({"id": 1}, {"$push": {"nam": answer}})

@dp.callback_query_handler(text='next_question')
async def next_question(call: types.CallbackQuery):
    await call.message.answer('Növbəti suala keçid')
@dp.callback_query_handler(text='cancel')
async def cancel(call: types.CallbackQuery):
    await call.message.answer('Dayandır')




@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)