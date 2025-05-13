import speech_recognition as sr

file_path = "filepath"

def transcribe_audio(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results from speech recognition service"
    
result = transcribe_audio(file_path)
print("🔊 Transcription Result:", result)