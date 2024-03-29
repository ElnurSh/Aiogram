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



button = InlineKeyboardButton('Next question', callback_data='next_question')
button1 = InlineKeyboardMarkup().add(button)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    try:
        quiz.delete_one({'user': message.from_user.id})
    except:
        pass
    quiz.insert_one({'user': message.from_user.id, 'qnumber': 1, 'index': 0, 'answer': 0, 'score': 0} )
    for num, text in enumerate(question1[1:4]):
        if text == question1[-1]:
            correct_index = num
            quiz.update_one({'user': message.from_user.id}, {'$set': {'index': correct_index}})
            correct_answer = text
            quiz.update_one({'user': message.from_user.id}, {'$set': {'answer': correct_answer}})
            await message.answer_poll(question=question1[0],
                                        options=question1[1:4],
                                        correct_option_id=correct_index,
                                        type='quiz',
                                        is_anonymous=False,
                                        #open_period=5,
                                        reply_markup=button1)



@dp.poll_answer_handler()
async def poll_answer(poll_answer: types.PollAnswer):
    if poll_answer.option_ids[-1] == quiz.find({'user': poll_answer.user.id}).distinct('index')[-1]:
        quiz.update_one({'user': poll_answer.user.id}, {'$set': {'score': int(quiz.find({'user': poll_answer.user.id}).distinct('score')[-1])+1}})



@dp.callback_query_handler(text='next_question')
async def next_question(call: types.CallbackQuery):
    if quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1] == 10:
        right = quiz.find({'user': call.from_user.id}).distinct('score')[-1]
        wrong = quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1] - quiz.find({'user': call.from_user.id}).distinct('score')[-1]
        await bot.answer_callback_query(call.id,
                                        text="Quiz FINISHED!\n"
                                             "Your score is:\n"
                                             f"👍 {right}\n"
                                             f"👎 {wrong}",
                                        show_alert=True)
    else:
        quiz.update_one({'user': call.from_user.id}, {'$set': {'qnumber': int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])+1}})
        for num, text in enumerate(globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])}"][1:4]):
            if text == globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])}"][-1]:
                correct_index = num
                quiz.update_one({'user': call.from_user.id}, {'$set': {'index': correct_index}})
                correct_answer = text
                quiz.update_one({'user': call.from_user.id}, {'$set': {'answer': correct_answer}})
                await bot.send_poll(chat_id=call.from_user.id,
                                question=globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])}"][0],
                                options=globals()[f"question{int(quiz.find({'user': call.from_user.id}).distinct('qnumber')[-1])}"][1:4],
                                correct_option_id=correct_index,
                                type='quiz',
                                is_anonymous=False,
                                # open_period=5,
                                reply_markup=button1)




@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)
