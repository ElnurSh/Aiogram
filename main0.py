from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import *
#from questions import *


cluster = MongoClient(MongoTOKEN)
db = cluster["Bot"]
quiz = db["Quiz"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

print(quiz.distinct('qnum')[0])

button = InlineKeyboardButton('Növbəti suala keçid', callback_data='next_question')
button1 = InlineKeyboardMarkup().add(button)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    quiz.insert_one({'user': message.from_user.id, 'score': 1 } )
    for num, text in enumerate(question1[1:4]):
        if text == question1[-1]:
            correct_index = num
            await message.answer_poll(question=question1[0],
                                        options=question1[1:4],
                                        correct_option_id=correct_index,
                                        type='quiz',
                                        is_anonymous=False,
                                        #open_period=5,
                                        reply_markup=button1)



@dp.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    answer = " ".join(map(str,poll_answer.option_ids))
    quiz.find_one_and_update({"id": 1}, {"$push": {"nam": answer}})

@dp.callback_query_handler(text='next_question')
async def next_question(call: types.CallbackQuery):
    for num, text in enumerate(globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('score')[-1])+1}"][1:4]):
        if text == globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('score')[-1])+1}"][-1]:
            correct_index = num
            await bot.send_poll(chat_id=call.from_user.id,
                                question=globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('score')[-1])+1}"][0],
                                options=globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('score')[-1])+1}"][1:4],
                                correct_option_id=correct_index,
                                type='quiz',
                                is_anonymous=False,
                                # open_period=5,
                                reply_markup=button1)
            quiz.update_one({'user': call.from_user.id}, {'$set': {'score': int(quiz.find({'user': call.from_user.id}).distinct('score')[-1])+1}})
    #await call.message.answer('Növbəti suala keçid')
@dp.callback_query_handler(text='cancel')
async def cancel(call: types.CallbackQuery):
    await call.message.answer('Dayandır')




@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
