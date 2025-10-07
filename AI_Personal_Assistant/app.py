from flask import Flask, request, jsonify, render_template
import datetime
import pyttsx3
import wikipedia
import spacy
import speech_recognition as sr

app = Flask(__name__)

engine = pyttsx3.init()
nlp = spacy.load("en_core_web_sm")


def speak(text):
    engine.say(text)
    engine.runAndWait()


def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening... Speak now!")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"✅ You said: {text}")
            return text
        except sr.UnknownValueError:
            print("❌ Sorry, I couldn't understand your voice.")
            return ""
        except sr.RequestError:
            print("⚠️ Speech recognition service unavailable.")
            return ""


def get_time():
    now = datetime.datetime.now().strftime("%I:%M %p")
    response = f"The current time is {now}."
    speak(response)
    return response


def get_day():
    today = datetime.datetime.now().strftime("%A")
    response = f"Today is {today}."
    speak(response)
    return response


def solve_math(query):
    try:
        expression = query.lower().replace("calculate", "").replace("what is", "").strip()
        result = eval(expression)
        response = f"The result is {result}."
    except Exception:
        response = "Sorry, I couldn’t solve that."
    speak(response)
    return response


def search_web(query):
    search_query = query.lower().replace("search", "").strip()
    try:
        wikipedia.set_lang("en")
        summary = wikipedia.summary(search_query, sentences=2)
        response = f"Here's what I found: {summary}"
    except wikipedia.DisambiguationError as e:
        response = f"Your query may refer to multiple things: {e.options[:5]}"
    except wikipedia.PageError:
        response = "Sorry, I couldn't find information on that topic."
    except Exception as e:
        response = "Sorry, there was an error searching the web."
        print("Wikipedia Search Error:", e)
    speak(response)
    return response


def set_reminder(query):
    response = f"Reminder noted: {query}"
    speak(response)
    return response


def process_command(text):
    text_lower = text.lower()

    if "time" in text_lower:
        return get_time()
    elif "day" in text_lower or "date" in text_lower:
        return get_day()
    elif "calculate" in text_lower or "what is" in text_lower:
        return solve_math(text_lower)
    elif "remind" in text_lower:
        return set_reminder(text)
    elif "search" in text_lower or any(kw in text_lower for kw in ["who", "what", "where", "when", "which"]):
        return search_web(text)
    else:
        response = "I'm not sure how to respond to that."
        speak(response)
        return response


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("query", "")
    response = process_command(query)
    return jsonify({"response": response})


if __name__ == "__main__":
    print("\n🤖 Welcome to Aayushi's AI Personal Assistant!")
    print("Choose mode:")
    print("1️⃣  Web Chat Mode (runs on browser)")
    print("2️⃣  Voice Mode (talk via microphone)")

    mode = input("Enter 1 or 2: ").strip()

    if mode == "1":
        print("\n🌐 Starting Web Mode... Visit: http://127.0.0.1:5000")
        app.run(debug=True)

    elif mode == "2":
        print("\n🗣️ Starting Voice Mode... Speak to your AI Assistant!\nSay 'exit' or 'stop' to quit.\n")
        while True:
            text = listen()
            if text:
                if "exit" in text.lower() or "stop" in text.lower():
                    speak("Goodbye! Have a nice day.")
                    print("👋 Exiting Voice Mode...")
                    break
                response = process_command(text)
                print(f"AI: {response}")
    else:
        print("Invalid choice. Please restart and select 1 or 2.")
