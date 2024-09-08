import pyttsx3
import speech_recognition as sr
import datetime
import os
import cv2
import random
from requests import get, RequestException
import wikipedia
import webbrowser
import pywhatkit as kit
import smtplib
import sys
import pyjokes
import pyautogui
import time
import requests
import instaloader
from googletrans import Translator
import fitz  # PyMuPDF
import psutil
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QThread
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from jarvisUi import Ui_jarvisUi  # Replace with your actual UI module

# Initialize the speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# Initialize the translator
translator = Translator()

# Text to speech
def speak(audio):
    engine.say(audio)
    print(audio)
    engine.runAndWait()

# To wish the user
def wish():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning SIR!")
    elif 12 <= hour < 18:
        speak("Good Afternoon SIR!")
    else:
        speak("Good Evening SIR!")
    speak("I am HAMAN SIR, please tell me how can I help you")

# Send email
def send_email(to, content, attachment_path=None):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        
        msg = MIMEMultipart()
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = to
        msg['Subject'] = content
        
        if attachment_path:
            filename = os.path.basename(attachment_path)
            attachment = open(attachment_path, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {filename}')
            msg.attach(part)
        
        server.sendmail(os.getenv('EMAIL_USER'), to, msg.as_string())
        server.close()
        speak("Email has been sent successfully!")
    except Exception as e:
        print(e)
        speak("Sorry sir, I am not able to send this email")

# Fetch news headlines
def fetch_news(api_key):
    main_url = f'http://newsapi.org/v2/top-headlines?sources=techcrunch&apiKey={api_key}'
    try:
        response = requests.get(main_url)
        response.raise_for_status()  # Check if the request was successful
        main_page = response.json()
    except RequestException as e:
        speak("There was an error fetching the news. Please try again later.")
        print(e)
        return
    
    articles = main_page.get("articles", [])
    if not articles:
        speak("No news articles found.")
        return

    head = []
    day = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth"]
    
    for ar in articles:
        head.append(ar["title"])
    
    for i in range(min(len(day), len(head))):
        speak(f"Today's {day[i]} news is: {head[i]}")

# Translate text to a different language
def translate_text(text, dest_language='en'):
    translation = translator.translate(text, dest=dest_language)
    return translation.text

# Read PDF file and extract text
def read_pdf(file_path):
    try:
        pdf_document = fitz.open(file_path)
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        print(e)
        return "Sorry, I couldn't read the PDF file."

class MainThread(QThread):
    def __init__(self):
        super(MainThread, self).__init__()
        self.cap = None  # Initialize the camera capture object

    def run(self):
        self.TaskExecution()

    def take_command(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 2
            audio = r.listen(source, timeout=2, phrase_time_limit=4)

        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}")
        except Exception as e:
            speak("Say that again please...")
            return "none"
        return query.lower()

    def open_camera(self):
        try:
            if self.cap is None or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(0)
                if self.cap.isOpened():
                    speak("Camera opened successfully.")
                else:
                    speak("Unable to open camera. Please check if it's connected.")
            else:
                speak("Camera is already open.")
        except Exception as e:
            print(f"Error opening camera: {e}")
            speak("Unable to open camera. Please check if it's connected.")

    def close_camera(self):
        try:
            if self.cap is not None and self.cap.isOpened():
                self.cap.release()
                cv2.destroyAllWindows()
                speak("Camera closed successfully.")
            else:
                speak("Camera is not open.")
        except Exception as e:
            print(f"Error closing camera: {e}")
            speak("Error closing camera. Please try again.")

    def TaskExecution(self):
        wish()
        while True:
            self.query = self.take_command().lower()

            # Logic building for tasks
            if "open vs code" in self.query:
                npath = "C:\\Users\\babar\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
                os.startfile(npath)

            elif "open notepad" in self.query:
                os.system("start notepad")

            elif "close notepad" in self.query:
                speak("Okay sir, closing notepad")
                os.system("taskkill /f /im notepad.exe")

            elif "open command prompt" in self.query:
                os.system("start cmd")

            elif "open camera" in self.query:
                self.cap = cv2.VideoCapture(0)
                while self.cap.isOpened():
                    ret, img = self.cap.read()
                    cv2.imshow("webcam", img)
                    if cv2.waitKey(50) & 0xFF == 27:  # 27 is the ASCII code for the ESC key
                        break
                self.cap.release()
                cv2.destroyAllWindows()

            elif "close camera" in self.query:
                if self.cap is not None and self.cap.isOpened():
                    self.cap.release()
                    cv2.destroyAllWindows()
                    speak("Camera closed successfully.")
                else:
                    speak("Camera is not open.")

            elif 'play music' in self.query or 'resume music' in self.query:
                music_dir = "C:\\Users\\babar\\Downloads\\Music"
                songs = os.listdir(music_dir)
                if songs:
                    song = random.choice(songs)
                    os.startfile(os.path.join(music_dir, song))

            elif "show ip address" in self.query:
                ip = get('https://api.ipify.org').text
                speak(f"Your IP address is {ip}")

            elif "wikipedia" in self.query:
                speak("Searching Wikipedia...")
                query = self.query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=2)
                speak("According to Wikipedia")
                speak(results)

            elif "open youtube" in self.query:
                webbrowser.open("www.youtube.com")

            elif "open facebook" in self.query:
                webbrowser.open("www.facebook.com")

            elif "open instagram" in self.query:
                webbrowser.open("www.instagram.com")

            elif "open github" in self.query:
                webbrowser.open("www.github.com")

            elif "open google" in self.query:
                speak("Sir, what should I search on Google?")
                cm = self.take_command().lower()
                webbrowser.open(f"http://google.com/search?q={cm}")

            elif "send message" in self.query:
                kit.sendwhatmsg("+92 306 8668460", "keep it up bro", 4, 14)
                speak("Message sent successfully!")

            elif "play music on youtube" in self.query or "play song" in self.query:
                kit.playonyt("song name")

            elif "tell me a joke" in self.query:
                joke = pyjokes.get_joke()
                speak(joke)

            elif "set alarm" in self.query:
                nn = datetime.datetime.now().hour
                if nn == 22:
                    music_dir = 'E:\\music'
                    songs = os.listdir(music_dir)
                    if songs:
                        os.startfile(os.path.join(music_dir, songs[0]))

            elif "shutdown the system" in self.query:
                os.system("shutdown /s /t 5")

            elif "restart the system" in self.query:
                os.system("shutdown /r /t 5")

            elif "sleep the system" in self.query:
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

            elif "switch the window" in self.query:
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(1)
                pyautogui.key
                pyautogui.keyUp("alt")

            elif "send email" in self.query:
                send_email(to="recipient@example.com", content="Email content here", attachment_path="path/to/attachment/file")

            elif "where am i" in self.query or "where are we" in self.query:
                try:
                    ip_add = get('https://api.ipify.org').text
                    url = f'https://get.geojs.io/v1/ip/geo/{ip_add}.json'
                    geo_requests = requests.get(url)
                    geo_data = geo_requests.json()
                    city = geo_data['city']
                    state = geo_data['region']
                    country = geo_data['country']
                    speak(f"Sir, I believe we are in {city} city, {state} state, {country} country.")
                except Exception as e:
                    speak("Sorry sir, I am not able to find where we are due to network issues.")

            elif "take screenshot" in self.query or "take a screenshot" in self.query:
                speak("Sir, please tell me the name for this screenshot file")
                name = self.take_command().lower()
                speak("Please sir, hold the screen for a few seconds. I am taking a screenshot.")
                time.sleep(3)
                img = pyautogui.screenshot()
                img.save(f"{name}.png")
                speak("I have saved the screenshot in our main folder. What's next?")

            elif "instagram profile" in self.query or "profile on instagram" in self.query:
                speak("Sir, please enter the username correctly.")
                name = self.take_command().lower()
                webbrowser.open(f"https://www.instagram.com/{name}")
                speak(f"Sir, here is the profile of the user {name}")
                time.sleep(5)
                speak("Sir, would you like to download the profile picture of this account?")
                condition = self.take_command().lower()

                if "yes" in condition:
                    try:
                        mod = instaloader.Instaloader()
                        mod.download_profile(name, profile_pic_only=True)
                        speak("The profile picture is saved in our main folder. What else can I do for you?")
                    except Exception as e:
                        speak("Sorry Sir, I encountered an error while downloading the profile picture.")
                        print(e)
                else:
                    speak("Alright Sir. Let me know if you need anything else.")

            elif "read pdf" in self.query:
                speak("Please tell me the path of the PDF file.")
                file_path = self.take_command().lower()  # Or get the file path through some other means
                pdf_content = read_pdf(file_path)
                speak("Here is the content of the PDF:")
                speak(pdf_content)

            elif "translate" in self.query:
                speak("Please tell me the sentence you want to translate.")
                sentence = self.take_command().lower()
                speak("In which language should I translate?")
                language = self.take_command().lower()

                # Define the language codes
                lang_codes = {
                    "spanish": "es",
                    "french": "fr",
                    "german": "de",
                    "hindi": "hi",
                    "italian": "it",
                    "japanese": "ja",
                    "korean": "ko",
                    "portuguese": "pt",
                    "russian": "ru",
                    "chinese": "zh-cn"
                }

                if language in lang_codes:
                    translated_text = translate_text(sentence, dest_language=lang_codes[language])
                    speak(f"The translation in {language} is: {translated_text}")
                else:
                    speak("Sorry, I do not support this language yet.")

            elif "tell me news" in self.query:
                speak("Please wait sir, fetching the latest news")
                fetch_news('your_news_api_key_here')
                speak("Here are the latest news")

            elif "battery" in self.query or "power" in self.query:
                battery = psutil.sensors_battery()
                percentage = battery.percent
                speak(f"Sir, our system has {percentage} percent battery remaining.")
                if percentage >= 75:
                    speak("We have enough power to continue our work.")
                elif 40 <= percentage < 75:
                    speak("We should connect our system to a charging point to charge our battery.")
                elif 15 <= percentage < 40:
                    speak("We don't have enough power to work. Please connect to charging.")
                elif percentage < 15:
                    speak("We have very low power. Please connect to charging, the system will shut down very soon.")

            elif "exit" in self.query or "quit" in self.query:
                speak("Thank you for using me, Sir. Have a great day!")
                sys.exit()

            # Handle any other tasks or commands here

            else:
                speak("Sorry, I didn't get that. Can you please repeat?")
            
            time.sleep(1)

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_jarvisUi()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)
        self.startExecution = MainThread()

    def startTask(self):
        self.ui.movie = QMovie("XDZT.gif")
        self.ui.label_2.setMovie(self.ui.movie)
        self.ui.movie.start()
        self.ui.movie = QMovie("Jarvis_Loading_Screen.gif")
        self.ui.label_3.setMovie(self.ui.movie)
        self.ui.movie.start()
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        label_time = current_time.toString("hh:mm:ss")
        label_date = current_date.toString(Qt.ISODate)
        self.ui.textBrowser.setText(label_date)
        self.ui.textBrowser_2.setText(label_time)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    jarvis = Main()
    jarvis.show()
    sys.exit(app.exec_())

