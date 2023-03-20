import tempfile
import soundfile as sf
import speech_recognition as sr
from playsound import playsound
import simpleaudio as sa
import numpy as np
from gtts import gTTS
import zhtts
from langdetect import detect



recognizer = sr.Recognizer()
ztts = zhtts.TTS()  # Initialize zhtts object

# play a beep and start detecting a wakeup word. play another beep when detected.
# this function will block
def detect_keyword(keyword:str):
    print(f"Listening for the keyword '{keyword}'...")
    while True:
        with sr.Microphone(sample_rate=44100) as source:
            try:
                audio_data = recognizer.listen(source, timeout=5)
                result = recognizer.recognize_sphinx(audio_data, keyword_entries=[(keyword, 1.0)])
                if keyword in result.lower():
                    print(f"Keyword {result} detected!")
                    return
            except sr.UnknownValueError:
                print(f"debug: UnknowValueError when recognizing speech")

                pass  # ignore if speech is not recognized
            except sr.WaitTimeoutError:
                print(f"debug: WaitTimeoutError when recognizing speech")
                pass  # ignore if no speech is detected during the timeout

# record a voice immediatly and play a beep sounds when stop is detected.
def record() -> str:
    with sr.Microphone(sample_rate=44100) as source:
        print("Calibrating microphone...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        dB = 30
        recognizer.energy_threshold += 10**(dB / 10)
        print("Recording started...")
        playsound("beep-07.wav")
        try:
            audio_data = recognizer.listen(source, timeout=3)
            print("Recording stopped.")
            playsound("beep-07.wav")
            # Convert the recorded audio data to a NumPy array
            audio_array = np.frombuffer(audio_data.get_raw_data(), dtype=np.int16)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                sf.write(temp_file.name, audio_array, 44100)
            return temp_file.name
        except sr.WaitTimeoutError:
            print("No one is speaking.")
            playsound("beep-02.wav")
            return ""

# this can generate either english or chinese
# The shortage of using zhtts is it doesn't speak any enligh, and I couldn't find any free chinese tts.
# for paid one, check Google Cloud TTS. (ask chatgpt for it)
def text_to_speech(text):
    language = detect(text)
    if language == 'zh-cn' or language == 'zh-tw' or language == 'ko':
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            ztts.text2wav(text, temp_file.name)
            print(f"Playing sound file... in {language}")
            playsound(temp_file.name)
    else:
        gtts = gTTS(text, lang=language)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
            gtts.save(temp_file.name)
            print(f"Playing sound file... in {language}")
            playsound(temp_file.name)

if __name__ == '__main__':
    while True:
        detect_keyword("iris")
        filename = record()
        playsound(filename)
