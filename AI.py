import speech_recognition as sr
import sounddevice as sd
from kokoro import KPipeline
from datetime import datetime
import numpy as np
from scipy.signal import resample_poly
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import time
import calendarGoogle
import os
import music as ms
class AI():
    skills = []
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
    #Configure Browser
    #Set The Path
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
    WOLFRAM_KEY_PATH = "wolfram-keys.txt"

    #WolframAlpha
    web_id = ""
    with open(WOLFRAM_KEY_PATH, "r") as f:
        web_id = f.readline().strip()

    wolframClient = wolframalpha.Client(web_id)
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
        self.m = sr.Microphone()

        if mic_name != "":
            mic_list = sr.Microphone.list_microphone_names()
            for index, name in enumerate(mic_list):
                if mic_name.lower() in name.lower():
                    self.m = sr.Microphone(device_index=index)
                    break
            
        self.r.energy_threshold = 2000 
        self.r.dynamic_energy_threshold = True
        
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
            raise ValueError("Must choose a proper voice from American English (voices that start with with 'a') Selection in Kokoro")
        elif value in self.__engine.getProperty('voices'):
            self.__voice = value
            self.__engine.setProperty('voice', self.__voice)
        else:
            raise ValueError(f"Chosen voice must be a pyttsx3 voice. List of possible voices: {self.__engine.getProperty('voices')}")

    @staticmethod
    def listOrDict(var):
        if isinstance(var, list):
            return var[0]['plaintext']
        return var['plaintext']

    @staticmethod
    def search_wiki(self, query = ''):
        searchResults = wikipedia.search(query)
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

    def speak(self, text):
        if self.__advanced_tts:
            target_sr = int(self.m.SAMPLE_RATE)
            def resample(audio):
                original_sr = 24000
                gcd = np.gcd(original_sr, target_sr)
                up = target_sr // gcd
                down = original_sr // gcd
                return resample_poly(audio, up, down)
             
            generator = self.__engine(text, voice=self.__voice)
            try:
                for i, (gs, ps, audio) in enumerate(generator):
                    sd.play(resample(audio), samplerate=target_sr)
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
                #List commands
                if query[0] == 'say':
                    query.pop(0)
                    speech = ' '.join(query)
                    self.speak(speech)
                elif query[0] == 'off':
                    self.speak("Shutting Down")
                    break

                #Navigation:
                elif query[0] == 'go' and query[1] == 'to':
                    self.speak('Opening...')
                    query = ' '.join(query[2:])
                    if '.' not in query:
                        query = query + ".com"
                    webbrowser.get().open_new(query)

                #Wikipedia
                elif query[0] == 'look' and query[1] == 'up':
                    query.pop(0)
                    query = ' '.join(query)
                    self.speak("Loading Data... Processing...")
                    self.speak(AI.search_wiki(query))

                #WolframAlpha
                elif query[0] == 'compute' or query[0] == 'calculate':
                    query = ' '.join(query[1:])
                    self.speak("computing")
                    try:
                        result = self.search_wolframalpha(query)
                        self.speak(result)
                    except:
                        self.speak("Unable to Compute")

                #Note taking
                elif ' '.join(query[:3]) == "create new log":
                    self.speak("Ready to log")
                    newNote = self.get_listening_result().lower()
                    curr_time = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

                    with open('note_%s.txt' % curr_time, 'w') as newFile:
                        newFile.write(newNote)
                    self.speak("Note has been written")
                
                #Music Player:
                elif "play" in query[:3]:
                    if "by" in query:
                        self.speak(f"Attempting to play {" ".join(query[query.index("play")+1:query.index("by")])} by {" ".join(query[query.index("by")+1:])}")
                        if not ms.search_and_play_spotify(" ".join(query[query.index("play")+1:query.index("by")]), " ".join(query[query.index("by")+1:])):
                            self.speak("Sorry, I couldn't find that song. Could you try repeating your command?")
                    else:
                        self.speak(f"Playing {" ".join(query[query.index("play")+1:])}")
                        if not ms.search_and_play_spotify(" ".join(query[query.index("play")+1:])):
                            self.speak("Sorry, I couldn't find that song. Could you try repeating your command?")
                
                elif "resume" in query:
                    result = ms.resume()
                    if not result:
                        self.speak("Music is already playing, sir")
                    else:
                        self.speak("Playback started")
                
                elif ("pause" in query or "off" in query) and "music" in query:
                    result = ms.pause()
                    if not result:
                        self.speak("Music is already off, sir")
                    


                #Scheduler
                elif "schedule" in query or "calendar" in query:
                    if query[0] == "remove":
                        calendarGoogle.remove(query[1:query.index("from")])
                    elif query[0] == "add":
                        start, end, date, name = calendarGoogle.parseEvent(" ".join(query[1:]))
                        if start == "No Break":
                            self.speak("Please use the work 'break' when adding to the calendar")
                        elif not start or not end or not date or not name:
                            self.speak("Could not add to calendar; please try again")
                        else: 
                            self.speak(f"Adding {name} to your schedule, sir")
                            calendarGoogle.add(start, end, date, name)
        os._exit(0)
    
    def search_wolframalpha(self, query=''):
        response = self.wolframClient.query(query)
        #@success: wolfram could resolve query
        #@numpods: number of results returned
        #pod: List of results. can contain subpods.
        if response['@success'] == 'false':
            return 'Could not compute'
        
        #query resolved
        result = ''
        
        #question
        pod0 = response['pod'][0]

        pod1 = response['pod'][1]
        # May contain the answer, highest confidence
        #If has title of result or definition or is primary, then its official result
        if(('result') in pod1['@title'].lower() or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower())):
            #Get the result:
            result = AI.listOrDict(pod1['subpod'])
            # remove the bracketed
            return result.split('(')[0]
        else:
            question = AI.listOrDict(pod0['subpod'])
            #try out wikipedia
            self.speak("Computation Failed; trying wikipedia.")
            return self.search_wiki(question)

def main():
    friday = AI(name="Friday", advanced_tts=True, mic_name="cmteck")
    friday.run()


main()