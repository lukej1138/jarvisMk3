import speech_recognition as sr
import sounddevice as sd
from kokoro import KPipeline
from datetime import datetime
import pyttsx3
import webbrowser
import wikipedia
import requests
from GoogleAPI.calendarGoogle import CalendarGoogle
import os
import music as ms
import ModelStorage.Classifier as Classifier
from dotenv import load_dotenv

load_dotenv()

class AI():
    voices = [
    "af_heart",
    "af_alloy",
    "af_aoede",
    "af_bella",
    "af_jessica",
    "af_kore",
    "af_nicole",
    "af_nova",
    "af_river",
    "af_sarah",
    "af_sky",
    "am_adam",
    "am_echo",
    "am_eric",
    "am_fenrir",
    "am_liam",
    "am_michael",
    "am_onyx",
    "am_puck",
    "am_santa"
]

    #WolframAlpha
    web_id = os.getenv("WOLFRAM_KEY")

    #Want to have different models depending on if the user wants an advanced version or not; so if they want the advanced version, we should use the advanced_speak, otherwise use baseline

    def __init__(self, advanced_tts=True, name=None, mic_name=""):
        if name is not None and name != "":
            self.__name = name.lower()
        else:
            self.__name = "jarvis"
        
        self.__advanced_tts = advanced_tts
        if advanced_tts:
            self.__engine = KPipeline(lang_code="a")
            self.__voice = "af_heart"
        else:
            self.__engine = pyttsx3.init()
            self.__voice = 'com.apple.speech.synthesis.voice.Daniel'
            self.__engine.setProperty('voice', self.__voice)
        
        self.r = sr.Recognizer()
        self.r.pause_threshold = 1.5
        self.m = sr.Microphone()

        if mic_name != "":
            mic_list = sr.Microphone.list_microphone_names()
            for index, name in enumerate(mic_list):
                if mic_name.lower() in name.lower():
                    self.m = sr.Microphone(device_index=index)
                    break
            
        self.r.energy_threshold = 2000 
        self.r.dynamic_energy_threshold = True
        self.__classifier = Classifier.Classifier("jarvis")
        
    @property
    def name(self):
        return self.__name
    
    @property
    def advanced_tts(self):
        return self.__advanced_tts

    @property
    def engine(self):
        if self.__advanced_tts:
            return "Kokoro"
        return "Pyttsx3"

    @property
    def voice(self):
        return self.__voice
    
    @name.setter
    def name(self, value):
        if value == "":
            raise ValueError("New Name For AI Must Not Be Empty")
        self.__name = value.lower()
    
    @advanced_tts.setter
    def advanced_tts(self, value):
        if value != True and value != False:
            raise TypeError("Only Boolean Inputs Allowed")
        self.__advanced_tts = value
        if value:
            self.__engine = KPipeline(lang_code="a")
            self.__voice = "af_heart"
        else:
            self.__engine = pyttsx3.init()
            self.__voice = 'com.apple.speech.synthesis.voice.Daniel'
            self.__engine.setProperty('voice', self.__voice)

    @voice.setter
    def voice(self, value):
        value = value.lower()
        if (self.__advanced_tts and value in self.voices):
            self.__voice = value
        elif self.__advanced_tts:
            raise ValueError(f"Must choose a proper voice from American English (voices that start with with 'a') Selection in Kokoro. Voice options: {AI.voices}")
        elif value in self.__engine.getProperty('voices'):
            self.__voice = value
            self.__engine.setProperty('voice', self.__voice)
        else:
            raise ValueError(f"Chosen voice must be a pyttsx3 voice. List of possible voices: {self.__engine.getProperty('voices')}")


    def speak(self, text):
        if self.__advanced_tts:
            target_sr = int(sd.query_devices(sd.default.device[1], 'output')['default_samplerate'])
            # def resample(audio):
            #     original_sr = 24000
            #     gcd = np.gcd(original_sr, target_sr)
            #     up = target_sr // gcd
            #     down = original_sr // gcd
            #     return resample_poly(audio, up, down)
             
            generator = self.__engine(text, voice=self.__voice)
            try:
                for i, (gs, ps, audio) in enumerate(generator):
                    sd.play(audio, samplerate=24000)
                    sd.wait()
            except Exception as e:
                if "PortAudio" not in str(e):  # Only show non-audio errors
                    print(f"Error: {e}")
            finally:
                sd.stop()
        else:
            self.__engine.say(text)
            self.__engine.runAndWait()
    
    def get_listening_result(self):
        with self.m as src:
            self.r.adjust_for_ambient_noise(src)
            try:
                print("Listening")
                base_speech = self.r.listen(src) #recorded input
                query = self.r.recognize_google(base_speech, language="en_us").lower() #processed input
                print(f"Heard: {query}")
                return query
            except Exception as e:
                return None
        return query
    def contact_server(self, query):
        url = "http://localhost:8080/classify"
        response = requests.post(url, json={"query": query})
        return response.json()
    
    def run(self):
        self.speak(f"Hey, I'm {self.__name}, you're virtual assistant! Just say my name and ask for a command, and I'll see what I can do.")
        while True:
            # Parse as list
            query = self.get_listening_result()
            if not query:
                continue

            query = query.split()

            if(self.__name == query[0] and len(query) > 1):
                query.pop(0)
                #Basic commands
                if query[0] == 'say':
                    query.pop(0)
                    speech = ' '.join(query)
                    self.speak(speech)
                    continue
                elif query[0] == 'off':
                    self.speak("Shutting Down")
                    break
                    
                request = self.contact_server(" ".join(query))
                if request["request"] == "UNKNOWN":
                    self.speak("Sorry, I didn't understand your command.")

                #Navigation:
                elif request["request"] == "WEBSITE-ACCESS":
                    self.speak('Attempting to Open...')
                    query = request["websitename"]
                    if "https://" not in query:
                        query = "https://" + query
                    if '.' not in query:
                        query = query + ".com"
                    print(webbrowser.open_new(query))

                #Wikipedia
                elif request["request"] == "WIKIPEDIA":
                    self.speak("Loading Data... Processing...")
                    self.speak(AI.search_wiki(request["query"]))

                #WolframAlpha
                elif request["request"] == "WOLFRAMALPHA":
                    self.speak("attempting calculations...")
                    try:
                        result = self.search_wolframalpha(request["query"])
                        self.speak(result)
                    except:
                        self.speak("failed to compute")

                #Note taking
                elif request["request"] == "NOTE-TAKING":
                    self.speak("Ready to log")
                    newNote = self.get_listening_result().lower()
                    curr_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

                    with open(f'note_{curr_time}.txt', 'w') as newFile:
                        newFile.write(newNote)
                    self.speak("Note has been written")
                
                #Music Player:
                elif request["request"] == "MUSIC-PLAY":
                    if request["artistname"] != "unknown":
                        self.speak(f"Attempting to play {request["songname"]} by {request["artistname"]}")
                        if not ms.search_and_play_spotify(request["songname"],request["artistname"]):
                            self.speak("Sorry, I couldn't find that song. Could you try repeating your command?")
                    else:
                        self.speak(f"Playing {request["songname"]}")
                        if not ms.search_and_play_spotify(request["songname"]):
                            self.speak("Sorry, I couldn't find that song. Could you try repeating your command?")
                
                elif request["request"] == "MUSIC-RESUME":
                    result = ms.resume()
                    if not result:
                        self.speak("Music is already playing.")
                    else:
                        self.speak("Playback started")
                
                elif request["request"] == "MUSIC-PAUSE":
                    result = ms.pause()
                    if not result:
                        self.speak("Music is already off.")
                    
                #Scheduler
                elif "CALENDAR" in request["request"]:
                    if request["request"] == "CALENDAR-REMOVE":
                        CalendarGoogle().remove(request["name"])
                    else:
                        start, end, date, name = CalendarGoogle().parseEvent(request)
                        if not start or not end or not date or not name:
                            self.speak("Could not add to calendar; please try again")
                        else:
                            self.speak(f"Adding {name} to your schedule, sir")
                            CalendarGoogle().add(start, end, date, name)
        os._exit(0)
    def search_wiki(self, query = ''):
        try:
            searchResults = wikipedia.search(query)
        except Exception as e:
            print(self.speak("Sorry, there was an error processing the wiki request."))
            print(e)

        if not searchResults:
            print("No wikipedia results")
            return "No Results Detected"
        try:
            wikiPage = wikipedia.page(searchResults[0])
        except wikipedia.DisambiguationError as e:
            wikiPage = wikipedia.page(e.options[0])
        print(wikiPage.title)
        wikiSummary = str(wikiPage.summary)
        return wikiSummary

    def search_wolframalpha(self, query):
        #@success: wolfram could resolve query
        #@numpods: number of results returned
        #pod: List of results. can contain subpods.
        url = f"http://api.wolframalpha.com/v2/query"

        params = {
        "input"  : query,
        "appid" : self.web_id,
        "output" : "json"
        }

        initial_response = requests.get(url=url, params=params)
        response = initial_response.json()['queryresult']
        if not response['success']:
            return 'Could not compute'
        #query resolved
        result = ''
        pod0 = response['pods'][0]

        for i in range(1, len(response['pods'])):
            pod = response['pods'][i]
            if pod['id'].lower() == 'result' or pod['id'].lower() == 'decimalapproximation':
                result = pod['subpods'][0]['plaintext']
                # remove the bracketed
                if pod['id'] == 'DecimalApproximation':
                    dot = result.index(".")
                    result = "Approximately " + result[:dot] + " point " + "-".join(str(result[dot+1:dot+6]))
                return result

        self.speak("Computation Failed; trying wikipedia.")
        return self.search_wiki(pod0['subpods'][0]['plaintext'])


def main():
    friday = AI(name="Friday", advanced_tts=True)
    friday.run()

main()