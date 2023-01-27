import openai

# OpenAI API Key
aiTOKEN = ''
# Get a Telegram bot token from the BotFather bot
botTOKEN = ''

openai.api_key = aiTOKEN


# Get a response from the GPT-3 (Text-Davinci-003)
def text_davinci003(user_question):
    response = openai.Completion.create(
                  model="text-davinci-003",
                  prompt=user_question,
                  temperature=0.9,
                  max_tokens=150,
                  top_p=1,
                  frequency_penalty=0,
                  presence_penalty=0.6,
                  stop=[" Human:", " AI:"]
                )
    ai_answer = response['choices'][0]['text'].strip()
    return ai_answer
