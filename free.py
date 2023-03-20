import sounddevice as sd
from playsound import playsound
import openai
import soundfile as sf
import sys
import tempfile
import utils
import os
sys.stdout.reconfigure(encoding='utf-8')

if os.getenv("OpenAIKey"):
    openai.api_key = os.getenv("OpenAIKey")
else:
    raise("please supply openAI API Key")


keyword = 'strawberry'


def conversation(user_voice_filename, chat_history):
    # Speech to text using openAI
    with open(user_voice_filename, "rb") as speech:
        print("Debug: Asking OpenAI to transcribe")
        text = openai.Audio.transcribe("whisper-1", speech).text
    print(f"You: {text}")
    
    chat_history += [{"role": "user", "content": text}]

    # chat
    print("Debug: Asking OpenAI to chat")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=chat_history,
        max_tokens=2000,
    ).choices[0].message.content

    chat_history += [{"role": "assistant", "content": response}]
    print(f"Assistant: {response}")

    # text to speech
    utils.text_to_speech(response)


chat_history = []

# play a sound indicate program is up and running
playsound("beep-10.wav")
while True:
    # this call will block until it hears the keyword
    utils.detect_keyword(keyword)

    # record voice input and save to file
    user_voice_filename = utils.record()

    while user_voice_filename: # if no voice input, go back to detecting mode.
        
        conversation(user_voice_filename, chat_history)
        user_voice_filename = utils.record()