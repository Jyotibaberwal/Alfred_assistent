import pyttsx3
import speech_recognition as sr
from datetime import datetime, timedelta
import time
import threading
import smtplib
import webbrowser
from email.message import EmailMessage
import email
from email.header import decode_header
import imaplib
import subprocess  
import pywhatkit
import requests
import operator
import pywhatkit as kit
import os
from googletrans import Translator, LANGUAGES
import requests


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.setProperty("rate", 180)

appointments = {}
todo_list = []
notes = []
listening = True

def speak(text):
    
    engine.say(text)
    engine.runAndWait()

def takeCommand(prompt=None):
   
    r = sr.Recognizer()
    with sr.Microphone() as source:
        if prompt:
            speak(prompt)
        print('Listening...')
        r.pause_threshold = 1
        r.energy_threshold = 200
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=10, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            speak("I didn't hear you clearly. Can you repeat?")
            return "none"
    try:
        print('Understanding...')
        query = r.recognize_google(audio, language='en-in')
        print(f'You said: {query}')
        return query.lower()
    except sr.UnknownValueError:
        speak("I did not understand. Can you say that again?")
        return "none"
    except Exception as e:
        print(f"Error: {str(e)}")
        speak("There was an error. Please try again.")
        return "none"

def schedule_appointment():
    
    title = takeCommand("Please tell me the title of the appointment, sir")
    if title == "none":
        return

    date_input = takeCommand("Please tell me the date of the appointment in the format: day month year, for example, 28 September 2024.")
    if date_input == "none":
        return

    try:
        date_obj = datetime.strptime(date_input, '%d %B %Y').date()
    except ValueError:
        speak("I couldn't understand the date format. Please try again.")
        return

    time_input = takeCommand("Please tell me the time of the appointment in 24-hour format like 14 30 for 2:30 PM.")
    if time_input == "none":
        return

    try:
        time_obj = datetime.strptime(time_input, '%H %M').time()
    except ValueError:
        speak("I couldn't understand the time format. Please try again.")
        return

    appointment_datetime = datetime.combine(date_obj, time_obj)
    if appointment_datetime <= datetime.now():
        speak("This appointment time has already passed. Please set a future time.")
        return

    appointments[appointment_datetime] = title
    speak(f"Your appointment for {title} is scheduled on {date_obj.strftime('%d %B %Y')} at {time_obj.strftime('%H:%M')}.")

    reminder_thread = threading.Thread(target=set_reminder, args=(appointment_datetime, title))
    reminder_thread.start()

def set_reminder(appointment_datetime, title):
    
    time_left = (appointment_datetime - datetime.now()).total_seconds()

    if time_left > 0:
        speak(f"A reminder will be set for your appointment: {title}")
        time.sleep(time_left)  
        speak(f"This is a reminder for your appointment: {title}. It is happening now.")
    else:
        speak(f"The appointment {title} is already overdue.")

def make_call():
    
    speak("Who would you like to call?")
    contact_name = takeCommand()

    contacts = {
        "chandan": "+918451920924",  
        "jane": "+12025550123"
    }

    if contact_name in contacts:
        number = contacts[contact_name]
        speak(f"Calling {contact_name} at {number}.")
        try:
          
            subprocess.call(["start", f"tel:{number}"], shell=True)
        except Exception as e:
            speak("There was an error making the call.")
            print(f"Error: {str(e)}")
    else:
        speak("I don't have this contact in my list.")


def send_message():
   
    speak("To whom do you want to send a message?")
    recipient = takeCommand()

    contacts = {
        "chandan": "+918451920924",  
        "jane": "+12025550123"  
    }

    if recipient in contacts:
        recipient_number = contacts[recipient]
    else:
        speak("I don't have this contact in my list.")
        return

    speak("What message would you like to send?")
    message = takeCommand()
    
    if message != "none":
        try:
           
            pywhatkit.sendwhatmsg(recipient_number, message, datetime.now().hour, datetime.now().minute + 1)
            speak("Your message has been sent.")
        except Exception as e:
            speak("There was an error while sending the message.")
            print(f"Error: {str(e)}")

def search_web(query=None):
    
    if not query:
        query = takeCommand("What would you like to search for on the web?")
        if query == "none":
            return
    
    webbrowser.open(f"https://www.google.com/search?q={query}")
    speak(f"Here is what I found for {query}.")

import re

def perform_calculation():
    """Performs basic arithmetic calculations with large numbers."""
    speak("What calculation would you like to perform? For example, 'add 100 and 200', 'subtract 50 from 300', or 'divide 1000 by 25'.")
    calculation = takeCommand()
    
    if "none" in calculation:
        speak("Sorry, I didn't catch that. Please repeat the calculation.")
        return

    try:
        
        if 'add' in calculation:
            numbers = [int(num) for num in re.findall(r'\d+', calculation)]
            result = sum(numbers)
            speak(f"The result of addition is {result}.")
        elif 'subtract' in calculation:
            numbers = [int(num) for num in re.findall(r'\d+', calculation)]
            result = numbers[0] - numbers[1]
            speak(f"The result of subtraction is {result}.")
        elif 'multiply' in calculation:
            numbers = [int(num) for num in re.findall(r'\d+', calculation)]
            result = numbers[0] * numbers[1]
            speak(f"The result of multiplication is {result}.")
        elif 'divide' in calculation:
            numbers = [int(num) for num in re.findall(r'\d+', calculation)]
            if numbers[1] != 0:
                result = numbers[0] / numbers[1]
                speak(f"The result of division is {result}.")
            else:
                speak("Sorry, you can't divide by zero.")
        else:
           
            result = eval(calculation)
            speak(f"The result is {result}.")
    except Exception as e:
        speak("Sorry, I could not perform the calculation. Please try again.")
        print(f"Calculation Error: {e}")

def play_music():
    """Plays music either from YouTube or a local folder."""
    speak("What song or artist would you like to listen to?")
    song = takeCommand()
    
    
    if song != "none":
        speak(f"Playing {song} on YouTube.")
        kit.playonyt(song)

def stop_music():
    """Stops music playback."""
    
    os.system("taskkill /IM chrome.exe /F")
    speak("Music stopped.")


def get_news_updates():
    """Fetches and speaks the latest news headlines."""
    api_key = "d17efa124a444fa0a4714043c86db759"  
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles')

            if articles:
                speak("Here are the latest news headlines:")
                for index, article in enumerate(articles[:5], start=1): 
                    title = article['title']
                    speak(f"{index}. {title}")
            else:
                speak("I couldn't find any news articles at the moment.")
        else:
            speak("Failed to retrieve news. Please check your internet connection or API key.")
    except Exception as e:
        print(f"Error fetching news: {e}")
        speak("Sorry, I couldn't fetch the news right now.")

def make_restaurant_reservation():
    
    speak("Which restaurant would you like to reserve a table at?")
    restaurant_name = takeCommand()
    
    if restaurant_name != "none":
        
        
        speak(f"Attempting to make a reservation at {restaurant_name}.")
       
    else:
        speak("I didn't catch the restaurant name.")

def translate_text():
    """Translates a text into a specified target language."""
    speak("Please tell me the text you want to translate.")
    text_to_translate = takeCommand()
    
    if "none" in text_to_translate:
        speak("Sorry, I didn't catch the text for translation.")
        return

    speak("Which language would you like to translate into? For example, French, Spanish, or Hindi.")
    target_language = takeCommand().lower()

    try:
        translator = Translator()
        target_language_code = None

        for lang_code, lang_name in LANGUAGES.items():
            if lang_name.lower() == target_language:
                target_language_code = lang_code
                break
        
        if target_language_code:
            translated_text = translator.translate(text_to_translate, dest=target_language_code).text
            speak(f"The translation in {target_language} is: {translated_text}")
        else:
            speak(f"Sorry, I don't support translation to {target_language} at the moment.")
    except Exception as e:
        speak("Sorry, I couldn't complete the translation. Please try again.")
        print(f"Translation Error: {e}")

def get_recipe_suggestion():
    
    speak("What dish would you like to make?")
    dish_name = takeCommand() 
    
    if "none" in dish_name:
        speak("Sorry, I didn't catch that. Please tell me the dish again.")
        return

    api_key = '3ccaca78398342e2b9ed9a01d003cf51'  
    url = f"https://api.spoonacular.com/recipes/complexSearch?query={dish_name}&apiKey={api_key}"

    try:
      
        response = requests.get(url)
        recipe_data = response.json()

       
        if response.status_code == 200:
            if recipe_data["results"]:
                speak(f"I found some recipes for {dish_name}.")
                for i, recipe in enumerate(recipe_data["results"][:3], 1): 
                    recipe_title = recipe['title']
                    recipe_id = recipe['id']
                    speak(f"Recipe {i}: {recipe_title}. Would you like to know the ingredients and instructions?")
                    
                    details_query = takeCommand()
                    if 'yes' in details_query:
                        get_recipe_details(recipe_id)  
            else:
                speak(f"Sorry, I couldn't find any recipes for {dish_name}.")
        else:
            speak(f"Error fetching recipes. Status code: {response.status_code}")
            print(f"Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        speak("There was an error connecting to the recipe service. Please try again later.")
        print(f"Recipe API Error: {e}")

def get_recipe_details(recipe_id):
    
    api_key = 'YOUR_SPOONACULAR_API_KEY'  
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"

    try:
        response = requests.get(url)
        recipe_details = response.json()

        if response.status_code == 200:
            ingredients = recipe_details["extendedIngredients"]
            instructions = recipe_details["instructions"]

            speak("Here are the ingredients you need:")
            for ingredient in ingredients:
                speak(ingredient['original'])
            
            speak("And here are the instructions to prepare the dish:")
            speak(instructions)
        else:
            speak(f"Error fetching recipe details. Status code: {response.status_code}")
            print(f"Error: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        speak("There was an error connecting to the recipe details service. Please try again later.")
        print(f"Recipe Details API Error: {e}")


def get_weather_report(location):
    
    api_key = "YOUR_WEATHER_API_KEY"  
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={location}&aqi=no"
    try:
        response = requests.get(url)
        weather_data = response.json()
        if response.status_code == 200:
            location_name = weather_data['location']['name']
            country = weather_data['location']['country']
            temperature = weather_data['current']['temp_c']
            condition = weather_data['current']['condition']['text']
            speak(f"The weather in {location_name}, {country} is {condition} with a temperature of {temperature}°C.")
        else:
            speak(f"Could not fetch weather for {location}.")
    except Exception as e:
        speak("Sorry, I could not fetch the weather report.")
        print(f"Weather Error: {e}")

def show_appointments():
    if not appointments:
        speak("You have no appointments scheduled.")
    else:
        speak("Here are your upcoming appointments:")
        for appt_time, title in sorted(appointments.items()):
            speak(f"{title} on {appt_time.strftime('%d %B %Y at %H:%M')}")

def send_email():
   
    try:
        speak("Who would you like to send the email to?")
        recipient = takeCommand().lower()
        if recipient == "chandan":
            recipient_email = "cm505551@gmail.com"
        else:
            speak("I don't have the email address of this person. Please add it to my contacts.")
            return

        speak("What should be the subject of the email?")
        subject = takeCommand()

        speak("What is the message?")
        message_body = takeCommand()

        email_message = EmailMessage()
        email_message['From'] = 'chandanmishrar9@gmail.com'  
        email_message['To'] = recipient_email
        email_message['Subject'] = subject
        email_message.set_content(message_body)
        
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.login('chandanmishrar9@gmail.com', 'sjol ltda xazd scwx')  
            smtp.send_message(email_message)

        speak("Your email has been sent successfully.")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        speak("There was an error while sending the email.")

def read_emails():
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login('chandanmishrar9@gmail.com', 'sjol ltda xazd scwx') 
        imap.select("inbox")
        status, messages = imap.search(None, "ALL")
        email_ids = messages[0].split()
        latest_email_id = email_ids[-1]
        status, msg_data = imap.fetch(latest_email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")
                from_ = msg.get("From")

                speak(f"Subject: {subject}")
                speak(f"From: {from_}")
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            speak("The message is: ")
                            speak(body)
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                    speak("The message is: ")
                    speak(body)
        imap.close()
        imap.logout()

    except Exception as e:
        print(f"Error: {str(e)}")
        speak("There was an error reading your emails.")

def add_to_do():
   
    task = takeCommand('What task would you like to add to your to-do list, sir?')
    if task != 'none':
        todo_list.append(task)
        speak(f"Task '{task}' has been added to your to-do list.")
def show_todo_list():
   
    if not todo_list:
        speak("Your to-do list is currently empty.")
    else:
        speak("Here are the tasks in your to-do list:")
        for index, task in enumerate(todo_list, start=1):
            speak(f"{index}. {task}")

        
        speak("Would you like to mark any task as completed? Please tell me the task number.")
        task_to_complete = takeCommand() 
        
        if task_to_complete.isdigit(): 
            task_index = int(task_to_complete) - 1 
            
            if 0 <= task_index < len(todo_list):  
                completed_task = todo_list.pop(task_index) 
                speak(f"Task '{completed_task}' has been marked as completed.")
            else:
                speak("Sorry, that task number is not valid.")
        else:
            speak("I didn't understand the task number. Please try again.")


def take_note():
    note = takeCommand("What would you like to note down?")
    if note != "none":
        notes.append(note)
        speak("Note added.")

def show_note():
   
    if not notes:
        speak("You have no notes.")
    else:
        speak("Here are your notes:")
        for index, note in enumerate(notes, start=1):
            speak(f"{index}. {note}")
def play_podcast():
    speak("Which podcast platform would you like to use? Spotify or Apple Podcasts?")
    service = takeCommand()
    if "spotify" in service:
        speak("Which podcast would you like to listen to?")
        podcast = takeCommand()
        webbrowser.open(f"https://open.spotify.com/search/{podcast}")
        speak(f"Playing {podcast} on Spotify.")
    elif "apple" in service:
        speak("Which podcast would you like to listen to?")
        podcast = takeCommand()
        webbrowser.open(f"https://podcasts.apple.com/search/{podcast}")
        speak(f"Playing {podcast} on Apple Podcasts.")
    else:
        speak("Sorry, I currently support Spotify and Apple Podcasts.")

def play_video():
    speak("Which platform would you like to use? YouTube, Netflix, or Prime Video?")
    service = takeCommand()
    if "youtube" in service:
        speak("What would you like to watch on YouTube?")
        video = takeCommand()
        webbrowser.open(f"https://www.youtube.com/results?search_query={video}")
        speak(f"Playing {video} on YouTube.")
    elif "netflix" in service:
        speak("Opening Netflix for you.")
        webbrowser.open("https://www.netflix.com")
    elif "prime video" in service:
        speak("Opening Prime Video for you.")
        webbrowser.open("https://www.primevideo.com")
    else:
        speak("I currently support YouTube, Netflix, and Prime Video.")
def open_social_media():
    speak("Which social media platform would you like to open? Facebook, Twitter, or Instagram?")
    platform = takeCommand()
    if "facebook" in platform:
        webbrowser.open("https://www.facebook.com")
        speak("Opening Facebook.")
    elif "twitter" in platform:
        webbrowser.open("https://www.twitter.com")
        speak("Opening Twitter.")
    elif "instagram" in platform:
        webbrowser.open("https://www.instagram.com")
        speak("Opening Instagram.")
    else:
        speak("I currently support Facebook, Twitter, and Instagram.")
def open_productivity_suite():
    speak("Which productivity suite would you like to use? Google Workspace or Microsoft 365?")
    suite = takeCommand()
    if "google" in suite:
        webbrowser.open("https://workspace.google.com")
        speak("Opening Google Workspace.")
    
    else:
        speak("I support Google Workspace and Microsoft 365.")

def open_fitness_tracking():
    speak("Which fitness tracking app would you like to open? Fitbit or Google Fit?")
    service = takeCommand()
    if "fitbit" in service:
        webbrowser.open("https://www.fitbit.com")
        speak("Opening Fitbit.")
    elif "google fit" in service:
        webbrowser.open("https://fit.google.com")
        speak("Opening Google Fit.")
    else:
        speak("I support Fitbit and Google Fit.")

def open_e_commerce():
    speak("Would you like to shop on Amazon or eBay?")
    platform = takeCommand()
    if "amazon" in platform:
        webbrowser.open("https://www.amazon.com")
        speak("Opening Amazon.")
    elif "ebay" in platform:
        webbrowser.open("https://www.ebay.com")
        speak("Opening eBay.")
    else:
        speak("I support Amazon and eBay.")
def open_travel_booking():
    speak("Which travel service would you like to use? Expedia or Booking.com?")
    service = takeCommand()
    if "expedia" in service:
        webbrowser.open("https://www.expedia.com")
        speak("Opening Expedia.")
    elif "booking.com" in service:
        webbrowser.open("https://www.booking.com")
        speak("Opening Booking.com.")
    else:
        speak("I support Expedia and Booking.com.")

def open_note_taking():
    speak("Would you like to use Google Keep or Evernote?")
    service = takeCommand()
    if "keep" in service:
        webbrowser.open("https://keep.google.com")
        speak("Opening Google Keep.")
    elif "evernote" in service:
        webbrowser.open("https://www.evernote.com")
        speak("Opening Evernote.")
    else:
        speak("I support Google Keep and Evernote.")


def process_query(query):
    if 'schedule_appointment' in query:
        schedule_appointment()
    
    elif 'show appointments' in query:
        show_appointments()

    elif 'send email' in query:
        send_email()

    elif 'read email' in query:
        read_emails()

    elif 'add to do' in query:
        add_to_do()

    elif 'show todo' in query:
        show_todo_list()

    elif 'make call' in query or 'call' in query:
        make_call()

    elif 'send message' in query or 'message' in query:
        send_message()

    elif 'take note' in query:
        take_note()

    elif 'show note' in query or 'show notes' in query:
        show_note()

    elif 'search' in query and 'web' in query:
        search_query = query.replace('search', '').replace('on the web', '').strip()
        search_web(search_query)
        

    elif 'calculate' in query:
        perform_calculation()

    elif 'weather update' in query:
        location = takeCommand("Which location's weather report would you like?")
        if location != "none":
            get_weather_report(location)

    elif 'play music' in query:
        play_music()

    elif 'stop music' in query:
        stop_music()

    elif 'news update' in query:
        get_news_updates()

    elif 'restaurant reservation' in query:
        make_restaurant_reservation()

    elif 'translate' in query:
        translate_text()

    elif 'recipe' in query or 'suggest recipe' in query or 'what should I cook' in query:
        get_recipe_suggestion()  
    elif 'podcast' in query:
        play_podcast()

    elif 'video'in query:
        play_video()
    
    elif 'social media' in query:
        open_social_media()
    elif 'productivity' in query:
        open_productivity_suite()
    elif 'shop' in query:
        open_e_commerce()
        

    elif 'exit' in query or 'stop' in query:
        speak("Goodbye!")
        return False
    
    return True


if __name__ == '__main__':
    speak("Hello sir, how can I assist you today?")
    
    while True:
        query = takeCommand()
        if query == "none":
            continue
        if "alfred" in query:
            query = query.replace("alfred", "").strip()
            if not process_query(query):
                break
        if "stop" in query or "exit" in query:
            speak("Thanks for using the assistant! Goodbye!")
            break
