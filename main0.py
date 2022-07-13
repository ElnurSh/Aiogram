from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import *
import time
from questions import *


cluster = MongoClient(MongoTOKEN)
db = cluster["Bot"]
quiz = db["Quiz"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

print(quiz.distinct('qnum')[0])
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
    for num, text in enumerate(question1[1:4]):
        if text == question1[-1]:
            correct_index = num
            await message.answer_poll(question=question1[0],
                                        options=question1[1:4],
                                        correct_option_id=correct_index,
                                        type='quiz',
                                        is_anonymous=False,
                                        #open_period=5,
                                        reply_markup=kb)





@dp.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    answer = " ".join(map(str,poll_answer.option_ids))
    quiz.find_one_and_update({"id": 1}, {"$push": {"nam": answer}})

@dp.callback_query_handler(text='next_question')
async def next_question(call: types.CallbackQuery):
    chat_id_ = call.from_user.id
    print(chat_id_)
    print(quiz.distinct('qnum')[0])
    for num, text in enumerate(globals()[f"question{int(quiz.distinct('qnum')[-1])+1}"][1:4]):
        if text == globals()[f"question{int(quiz.distinct('qnum')[-1])+1}"][-1]:
            correct_index = num
            await bot.send_poll(chat_id=chat_id_,
                                question=globals()[f"question{int(quiz.distinct('qnum')[-1])+1}"][0],
                                options=globals()[f"question{int(quiz.distinct('qnum')[-1])+1}"][1:4],
                                correct_option_id=correct_index,
                                type='quiz',
                                is_anonymous=False,
                                # open_period=5,
                                reply_markup=kb)
            quiz.find_one_and_update({"id": 1}, {"$push": {"qnum": int(quiz.distinct('qnum')[-1])+1}})
    #await call.message.answer('Növbəti suala keçid')
@dp.callback_query_handler(text='cancel')
async def cancel(call: types.CallbackQuery):
    await call.message.answer('Dayandır')




@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)