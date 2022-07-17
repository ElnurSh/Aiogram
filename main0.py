from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from config import *
from questions import *
import certifi


cluster = MongoClient(MongoTOKEN, tlsCAFile=certifi.where())
db = cluster["Bot"]
quiz = db["Quiz"]

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)



button = InlineKeyboardButton('Növbəti suala keçid', callback_data='next_question')
button1 = InlineKeyboardMarkup().add(button)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    try:
        quiz.delete_one({'user': message.from_user.id})
    except:
        pass
    quiz.insert_one({'user': message.from_user.id, 'score': 0, 'qnumber': 1} )
    for num, text in enumerate(question1[1:4]):
        if text == question1[-1]:
            correct_index1 = num
            quiz.update_one({'user': message.from_user.id}, {'$set': {'index1': correct_index1}})
            correct_text1 = text
            quiz.update_one({'user': message.from_user.id}, {'$set': {'answer1': correct_text1}})
            await message.answer_poll(question=question1[0],
                                        options=question1[1:4],
                                        correct_option_id=correct_index1,
                                        type='quiz',
                                        is_anonymous=False,
                                        #open_period=5,
                                        reply_markup=button1)



@dp.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    if poll_answer.option_ids == quiz.find({'user': poll_answer.user.id}).distinct('index1')[-1]:
        quiz.update_one({'user': poll_answer.user.id}, {'$set': {'score': int(quiz.find({'user': poll_answer.user.id}).distinct('score')[-1])+1}})

        #ccc = quiz.find({'user': poll_answer.chat_id}).distinct('score')
        #ccc += 1
        #quiz.update_one({'user': poll_answer.user.id}, {'$set': {'score': ccc}})

    #answer = " ".join(map(str,poll_answer.option_ids))
    #quiz.find_one_and_update({"id": 1}, {"$push": {"nam": answer}})

@dp.callback_query_handler(text='next_question')
async def next_question(call: types.CallbackQuery):
    if quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1] == 3:
        await bot.answer_callback_query(call.id,
                                        text=f"Это был {quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1]} вопрос\n😉",
                                        show_alert=True)
    for num, text in enumerate(globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])+1}"][1:4]):
        if text == globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])+1}"][-1]:
            correct_index2 = num
            correct_text2 = text
            await bot.send_poll(chat_id=call.from_user.id,
                                question=globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])+1}"][0],
                                options=globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])+1}"][1:4],
                                correct_option_id=correct_index2,
                                type='quiz',
                                is_anonymous=False,
                                # open_period=5,
                                reply_markup=button1)
            quiz.update_one({'user': call.from_user.id}, {'$set': {'qnumber': int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])+1}})


#await call.message.answer('Növbəti suala keçid')

@dp.callback_query_handler(text='cancel')
async def cancel(call: types.CallbackQuery):
    await call.message.answer('Dayandır')




@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
