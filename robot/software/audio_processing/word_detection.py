import speech_recognition
import pyttsx3

# object that recognizes microphone audio
recognizer = speech_recognition.Recognizer()

while True:
    # try:
        with speech_recognition.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2) 
            # listen for 0.2 sec before recognizing to set noise threshold
            audio = recognizer.listen(mic)

            text = recognizer.recognize_google(audio)
            text = text.lower()

            print(text)

    # except speech_recognition.UnknownValueError():

    #     recognizer = speech_recognition.Recognizer()
    #     continue