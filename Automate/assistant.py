import pyttsx3 #pyttsx3 is a text-to-speech conversion library in Python
import speech_recognition as sr #Library for performing speech recognition
import pyaudio #To Handle Microphone
import wikipedia  #It will search queries from wikipedia 
import webbrowser #It will be used to visit sites through browser
import os # This will be used to do operating system related work
import datetime #For Date And Time
import automate
import pyautogui
import py_compile
import shutil
import tempfile
import time
import tempfile
import sys
import random
import nltk
import settings
from pytube import YouTube


DEFAULT_DIR = os.path.join (os.environ.get("APPDATA"),"automate")
TMP_DIR = tempfile.gettempdir()
TMP_PATH = os.path.join(TMP_DIR,"automate-exe.pyc")

if os.path.isdir(DEFAULT_DIR) == False:
    #Directory Will created
    os.mkdir(DEFAULT_DIR)
    os.mkdir(os.path.join(DEFAULT_DIR,"images"))

engine = pyttsx3.init("sapi5") 
#Microsoft Speech API (SAPI5) is the technology for voice recognition.
#We have created object of pyttsx3

#Now we will set the voice property of our assistant 

voices = engine.getProperty('voices') 

#By default we have set the voice property to a male voice 
#But we will provide a command below so that user can adjust the voice property (either male or female Voice)
voiceid = settings.CONFIG.getint('DEFAULT', 'voiceid')
engine.setProperty('voice', voices[voiceid].id)


#By default we have set the rate property to 150
rate = engine.getProperty('rate')
engine.setProperty('rate',180)

#By default we have set the volume peoperty to 1
volume = engine.getProperty('volume')
engine.setProperty('volume',2)

#This Speak function will enable our assistant to speak
def speak(audio):
   engine.say(audio) 
   #To convey the message in audio 
   engine.runAndWait() 

#This Greet function will greet the user
def greet():
    time = int(datetime.datetime.now().hour)
    if time >= 0 and time < 12:
        speak("Good Morning!")
    elif time >= 12 and  time < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    time = datetime.datetime.now().strftime("%H:%M")
    speak(f"Its : {time}")
    speak("I am your personal assistant!")
    speak("How may I help you?")

#Voice Recognition Module

#This function takes input from microphone and returns query 
def getCommand():
    #Recoginzer class will help us to recognize audio
  
    r = sr.Recognizer()

    with sr.Microphone() as source:
        #This pause_threshold will make assistant wait for 1 second if there is no sound
        r.pause_threshold = 0.5 
        audio = r.listen(source) #Listening to user
    #Now It is trying to recognize the audio
    try:
        #This is trying to recognize audio 
        query = r.recognize_google(audio,language='en-PK')
    except Exception as e:
        #if error occurrs 
        r = sr.Recognizer()
        return "None"
    return query
#END Voice Recognition Module

#Command Verfication Module And Command Execution Module
if __name__ == "__main__":
    greet()
        
    #Code to execute user commands
    while True:
        try:
            cmdc = getCommand()
            cmd = cmdc.lower()

            tokens = nltk.word_tokenize(cmd)
            if "assistant" in tokens:
                #this is to get the info of something from wikipedia
                if "change" in tokens and "voice" in tokens:
                    #Setting male voice
                    speak("OK!")
                    voices = engine.getProperty('voices') 
                    n = random.randint(0,len(voices) - 1)
                    for voice in voices:
                        if(voice.id == voices[n].id):
                            n = random.randint(0,len(voices) - 1)
                    engine.setProperty('voice', voices[n].id)
                    settings.CONFIG['DEFAULT']['voiceid'] = str(n)
                    settings.save_config()
                    speak("Done")
                elif "wikipedia" in tokens:
                    speak("What do you want to search from Wikipedia!")
                    searchitem = getCommand()
                    speak('Searching WikiPedia.....Please Wait!')
                    #it will get info from wikipedia
                    try:
                        response = wikipedia.summary(searchitem,sentences=2)
                        speak("Wikipedia Says")
                        speak(response)
                    except:
                        speak("Sorry No Information Found!")
                        continue

                
                elif "visit" in tokens and "youtube" in tokens:
                    #this is to open youtube on browser
                    speak("I am on It!")
                    webbrowser.open("https://youtube.com")
                elif ("visit" in tokens) and ("facebook" in tokens or "fb" in tokens):
                    speak("Wait a second. I am on it!")
                    #this is to open facebook on browser
                    webbrowser.open("https://facebook.com")
                elif "visit" in tokens and "google" in tokens:
                    speak("Wait a second!")
                    #this is to open google on browser
                    webbrowser.open("https://google.com")
                elif "visit" in tokens and "twitter" in tokens:
                    #this is to open twitter on browser
                    speak("I am on it. Please wait!")
                    webbrowser.open("https://twitter.com")
                elif "visit" in tokens and "yahoo" in tokens:
                    #this is to open yahoo on browser
                    speak("Wait a moment please. I am on it!")
                    webbrowser.open("https://yahoo.com")
                elif "visit" in tokens and ("instagram" in tokens or "insta" in tokens):
                    #this is to open instagram on browser
                    speak("Just give me a sec. I am on it!")
                    webbrowser.open("https://instagram.com")
                elif "restart" in tokens:
                    #this is to restart the computer
                    speak("Your PC will be Restarted in a moment!") 
                    os.system("shutdown /r")
                elif "shutdown" in tokens:
                    #this is to restart the computer
                    speak("I am on it!")
                    os.system("shutdown /s")
                elif "search" in tokens and "google" in tokens:
                    #To search on google
                    speak("What do you want to search on google?")
                    searchitem = getCommand()
                    speak("Ok. Wait a second please!")
                    webbrowser.open("https://google.com/search?q="+searchitem)
                elif "search" in tokens and "youtube" in tokens:
                    #To performing search operation on youtube
                    speak("What do you want to search on youtube?")
                    searchitem = getCommand()
                    speak("Give a sec please!")
                    webbrowser.open("https://youtube.com/search?q="+searchitem)
                elif "search" in tokens and "yahoo" in tokens:
                    #Searching from yahoo
                    speak("What do you want to search?")
                    searchitem = getCommand()
                    speak("I am on it!")
                    webbrowser.open("https://yahoo.com/search?q="+searchitem)
                elif "search" in tokens and "bing" in cmd:
                    #Performing Search operation from bing
                    speak("What do you want to search?")
                    searchitem = getCommand()
                    speak("Ok!")
                    webbrowser.open("https://bing.com/search?q="+searchitem)
                elif "open" in tokens and "whatsapp" in tokens:
                    #this is to open instagram on browser
                    speak("Right! I am on it! It may need your mobile have internet connection!")
                    try:    
                        import pywhatkit
                        pywhatkit.open_web()
                    except:
                        speak("Sorry could not open whatsapp!")
                elif "play" in tokens and "music" in tokens:
                    #this is to change the music folder
                    try:
                        speak("Please wait a moment!")
                        music_dir = settings.CONFIG.get('DEFAULT', 'musicdir')
                        if music_dir == "":
                            music_dir = os.path.join(os.environ['USERPROFILE'],"Music")
                            settings.CONFIG['DEFAULT']['musicdir'] = str(music_dir)
                            settings.save_config()
                        songs = os.listdir(music_dir)
                        sizesong = len(songs)
                        if sizesong > 0:
                            n = random.randint(0,sizesong-1)
                            print(songs[n])
                            os.startfile(os.path.join(music_dir,songs[n]))
                            print(os.path.join(music_dir,songs[n]))
                        else:
                            speak("Music Directory Is Empty!")
                    except:
                        speak("sorry could not play music")
                elif "change" in tokens and "music" in tokens and ("folder" in tokens or "directory" in tokens):
                    #this is to change the music folder
                    speak("Please wait a moment!")
                    music_dir = settings.CONFIG.get('DEFAULT', 'musicdir')
                    if music_dir == "":
                        music_dir = os.path.join(os.environ['USERPROFILE'],"Music")
                    newmusicdir = pyautogui.prompt(text='provide path to music folder', title='Change Music Directory!' , default=music_dir)
                    if (os.path.isdir(newmusicdir) == False):
                        speak("Sorry! Unbale to locate the provided directory. Music directory will be set to default path!")
                        settings.CONFIG['DEFAULT']['musicdir'] = music_dir
                        settings.save_config() 
                    else:
                        speak("Music Directory Updated Successfully!")
                        settings.CONFIG['DEFAULT']['musicdir'] = newmusicdir
                        settings.save_config()
                elif "play" in tokens and "youtube" in tokens:
                    speak("What do you want to play on youtube?")
                    searchitem = getCommand()
                    try:    
                        import pywhatkit
                        pywhatkit.playonyt(searchitem, True,True)
                    except:
                        speak("Sorry could not play the requested video!")
                    
                elif "take" in tokens and "screenshot"  in tokens:
                    delay = pyautogui.prompt(text="Delay Time for Screenshot:", title='Delay Time!' , default="2") 
                    if (delay.isnumeric() == False):
                            delay = "2"
                    pathpic = os.path.join(os.environ['USERPROFILE'],"Pictures")
                    pywhatkit.take_screenshot(os.path.join(pathpic,str(datetime.datetime.now()).replace(":","-")+".png"),int(delay))
                    speak("ScreenShot Taken! Screenshot is saved in Pictures Folder!")
                elif "download" in tokens and ("videos" in tokens or "video" in tokens) and "youtube" in tokens:
                    speak("Please provide youtube video links!")
                    link = pyautogui.prompt(text="Youtube Video Links:", title='Video Links' , default="links") 
                    try:  
                       yt = YouTube(link).streams.first().download(os.path.join(os.environ['USERPROFILE'],"Videos")) 
                       speak("video downloaded!")
                    except: 
                          #to handle exception 
                          speak("Connection Error") 
                elif "ok" in tokens or "thanks" in tokens or "goodbye" in tokens or "bye" in tokens or "thank" in tokens:
                    endgreet= ["Stay happy","Thanks", "Thank you", "Bye", "Ok"]
                    n = random.randint(0,len(endgreet) - 1)
                    speak(endgreet[n])
                elif "time" in tokens:
                    #this is to check the time
                    time = datetime.datetime.now().strftime("%H:%M")
                    speak(f"It's : {time}")
                elif "open" in tokens:
                    #this is to run applications
                    #Parsing the name of the application
                    speak("Which application do you want to open?")
                    exefile = getCommand()
                    speak("This may take time please wait!")
                    #splitting the name incase fullname is not found
                    filenames = exefile.split(" ")
                    #parsing the fullname in camel-case format
                    qexefile  = ""
                    for f in filenames:
                        #Making first letter as uppercase and joining different part which was split
                        qexefile = qexefile +  f[0].upper() + f[1:]
                        #to add space b/w each part of the name
                        qexefile = qexefile + " "
                    #removing the last " " as that is extra space
                    qexefile = qexefile[0:len(qexefile)-1]
                    #adding .exe and lnk (for shortcuts) so that we can search 
                    qexefilex = qexefile + ".exe"
                    exefilex = exefile + ".exe"
                    qexefilel = qexefile + ".lnk"
                    exefilel = exefile + ".lnk"
                    filename = ""
                    #result is used as the resultant path searched
                    result = ""
                    #Now searching the app with fullname 
                    for root, dir, files in os.walk("c:\\"):
                            if exefilel in files:
                                result = os.path.join(root, exefilel)
                                break
                            elif qexefilel in files:
                                result = os.path.join(root, qexefilel)
                                break
                            elif exefilex in files:
                                result = os.path.join(root, exefilex)
                                break
                            elif qexefilex in files:
                                result = os.path.join(root, qexefilex)
                                break
                    #if path found then running the app
                    if result != "":
                        speak("Opening" + exefile)
                        os.startfile(result)
                    #otherwise searching for app using different parts of the fullname
                    else:
                        # i is a check which is used to indicate whether app path was found or not
                        i = 0
                        for filename in filenames:
                            #for lowercase
                            filename = filename + ".exe"
                            #for uppercase
                            filename2 = filename[0].upper() + filename[1:]
                            result = ""
                            for root, dir, files in os.walk("c:\\"):
                                if filename in files:
                                    result = os.path.join(root, filename)
                                    i = i + 1
                                    break
                                elif filename2 in files:
                                    result = os.path.join(root, filename2)
                                    i = i + 1
                                    break
                            #if path found then run the app
                            if result != "":
                                speak("Opening " + exefile)
                                os.startfile(result)
                                break
                        #if app path could not be found 
                        if i == 0:
                            speak("No such application found to be executed!")
                elif "automate" in tokens:
                    #To automate tasks
                    speak("Please wait!")
                    app = automate.Automate(0)
                    app.MainLoop()
                elif ("run" in tokens or "execute" in tokens) and ("task"  in tokens or "program" in tokens or "file" in tokens):
                    #Parsing the name of the custom command
                    speak("Which task you want to execute?")
                    macrofile = getCommand()
                    speak("I am on it!")
                    filepath = os.path.join(DEFAULT_DIR,macrofile )
                    if os.path.exists(filepath) == True:
                        count = pyautogui.prompt(text='How many times do you want to run this task?', title='Count' , default='1')
                        if (count.isnumeric() == False):
                            count = "1"
                        capture = py_compile.compile(filepath)
                        shutil.copy(capture,TMP_PATH)
                        for x in range(int(count)):  
                            os.system(TMP_PATH)
                    else:
                        speak("Sorry!There is no such command or task!")
                else:
                    continue
        except Exception as e:
            print(e)
            continue


