from flask import Flask, render_template, request,redirect
import speech_recognition as sr
import pyttsx3
import datetime
import wikipedia
import pyjokes
import requests
import json
import sys
from textblob import TextBlob
import smtplib
import ssl
from email.message import EmailMessage

app = Flask(__name__)

# Initialize the Text-to-Speech engine
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty('voice', voices[1].id)

# Initialize the Speech Recognition engine
listener = sr.Recognizer()

# Function to analyze sentiment of text using TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = blob.sentiment.polarity
    return sentiment_score

# Function to send email notification
def send_email(receiver_email, subject, body, sender_email, sender_password):
    em = EmailMessage()
    em['From'] = sender_email
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender_email, sender_password)
        smtp.send_message(em)

# Function to recognize user commands through speech
def user_commands():
    command = ""  # Initialize command variable with a default value
    try:
        with sr.Microphone() as source:
            print("Start Speaking!!")
            voice = listener.listen(source)
            command = listener.recognize_google(voice)
            command = command.lower()
            if 'sara' in command:
                command = command.replace('sara', '')
                print(command)
    except sr.UnknownValueError:
        # Handle case where speech cannot be recognized
        print("Could not understand the audio.")
    except sr.RequestError as e:
        # Handle case where speech recognition service is unavailable
        print("Could not request results from the speech recognition service; {0}".format(e))
    return command
def send_notification(sentiment_score):
    if sentiment_score < -0.5:
        message = "Your child seems upset. Consider checking in with them."
    elif sentiment_score > 0.5:
        message = "Your child appears to be very happy. It's a good time to engage with them."
    else:
        message = "Your child's mood seems neutral."
    
    # Send notification email to the parent
    sender_email = "priyangasp2911@gmail.com"
    sender_password = "npnj jira zzjo kjct"  # Add your email password here
    receiver_email = "jameskalam999@gmail.com"
    subject = "Child Sentiment Analysis"
    
    send_email(receiver_email, subject, message, sender_email, sender_password)

# Example usage:
sentiment_score = 0.6  # Example sentiment score
send_notification(sentiment_score)


# Function to run the virtual assistant and perform actions based on user commands
def run_sara(command):
    if 'play' in command:
        song = command.replace('play', '')
        engine_talk('Playing' + song)
        # You can implement pywhatkit.playonyt(song) here
    elif 'time' in command:
        time = datetime.datetime.now().strftime('%I:%M %p')
        engine_talk('The current time is' + time)
    elif 'who is' in command:
        name = command.replace('who is', '')
        info = wikipedia.summary(name, 1)
        print(info)
        engine_talk(info)
    elif 'joke' in command:
        engine_talk(pyjokes.get_joke())
    elif 'weather' in command:
        engine_talk('Please tell the name of the city')
        city = user_commands()
        weather_api = weather(city)
        engine_talk(weather_api + 'degree fahreheit')
    elif 'stop' in command:
        sys.exit()
    else:
        # Analyze sentiment of the command and send notification to parent
        sentiment_score = analyze_sentiment(command)
        print(sentiment_score)
        if command.strip():
            send_notification(sentiment_score)
        engine_talk('I could not hear you properly')

# Function to speak out the response
def engine_talk(text):
    engine.say(text)
    engine.runAndWait()

# Function to fetch weather data from OpenWeatherMap API
def weather(city):
    api_key = "ba3a786cc56d0fa48b9837d79fff275d"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    city_name = city
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        return str(current_temperature)
    else:
        print(" City Not Found ")

# Main route
@app.route("/")
def hello():
    if request.method == "POST":
        # Handle the POST request here
        # For example, you can retrieve the user's command and process it
        command = request.form.get("command")
        run_sara(command)
        return "Success"
    else:
        # If it's a GET request, render the template as usual
        return render_template("alexa.html")  # Assuming template file is named template.html and located in the templates folder


@app.route("/home")
def home():
    return redirect('/')


# POST route for user commands
@app.route("/command", methods=["POST"])
def command():
    #data = request.get_json()
    command = request.form.get("command")
    #command = data["command"]
    run_sara(command)
    return "Success"

if __name__ == "__main__":
    app.run(debug=True)