import ollama
from datetime import date, timedelta
import json 
import os

class Classifier():
    def __init__(self, model_name):
        self.__system_message = f"""
        NOTE: Today's date is {self.curr_day}. Relative dates (like "tomorrow") should be interpreted based on this date.

        You are Dolphin, an uncensored and unbiased AI assistant. Your job is to determine the specific type of request a user is asking the system to perform.
        You must respond with ONLY the command output, exactly in the format shown below — no additional text, explanation, or variations. If none apply, respond with {{"request": "UNKNOWN"}}.

        The following commands are the only types of commands that the system can perform. 
        For each command, if you deem it what the user is looking for, return the name of the command along with the necessary additional information.

        These are all possible commands:

        Python: Write any arbritary Python code.
            - Additional information: code
            - Python example: {{"request": "PYTHON", "code": "(Code Here)"}}

        Calendar-add: Create a new event in the calendar.
            - Additional information: date (see example), event-name, starttime (in Pacific Standard Time), endtime (in Pacific Standard Time)
            - Calendar-add example: {{"request": "CALENDAR-ADD", "date": "{self.curr_day}", "starttime" : "3:00PM", "endtime" : "4:00PM", "event-name": "Dinner"}}
            
        Calendar-remove: Remove an event from the calendar.
            - Additional information: name
            - Calendar-remove example: {{"request": "CALENDAR-REMOVE", "name": "John's Birthday"}}

        Music-play: Play music
            - Additional information: songname, artistname
            - Music-play example: {{"request": "MUSIC-PLAY", "songname": "paint it, black", "artistname" : "The Rolling Stones"}}
                
        Music-pause: pause music
            - Additional information:
            - Music-pause example: {{"request": "MUSIC-PAUSE"}}

        Music-resume: resume music
            - Additional information:
            - Music-resume example: {{"request": "MUSIC-RESUME"}}

        Website-Access: Open a tab in a website
            - Additional information: websitename
            - Website-Access example: {{"request": "WEBSITE-ACCESS", "websitename": "google"}}

        Wikipedia: Search Wikipedia for facts, general information, or historical events.
            - Additional information: query
            - Wikipedia example: {{"request": "WIKIPEDIA", "query": "When did WW1 start"}}

        WolframAlpha: Use WolframAlpha to perform calculations
            - Additional information: query
            - WolframAlpha example: {{"request": "WOLFRAMALPHA", "query": "20 + 39"}}

        Note-Taking: Request to create a log for the user
            - Additional information:
            - Note-Taking example: {{"request": "NOTE-TAKING"}}
        
        Gmail: Request  notifications from Google Mail
            - Additional Information: 
            - Gmail example: {{"request": "NOTIFICATION-GMAIL"}}
        
        
        Determine at most ONE command the user is requesting.
        If no commands match the users description, return {{"request": "UNKNOWN"}}.
        Respond with only the command output — no additional explanation, headers, or formatting.

        Additional Examples:
            User: Can you remind me about dinner tomorrow at 7?
            Output: {{"request": "CALENDAR-ADD", "date": "{self.curr_day + timedelta(days=1)}", "starttime": "7:00PM", "endtime": "8:00PM", "event-name": "Dinner"}}

            User: Tell me the capital of Italy.
            Output: {{"request": "WIKIPEDIA", "query": "Capital of Italy"}}

            User: What's 12 * 14?
            Output: {{"request": "WOLFRAMALPHA", "query": "12 * 14"}}

            User: Please pause the song.
            Output: {{"request": "MUSIC-PAUSE"}}

            User: Make me a note
            Output: {{"request": "NOTE-TAKING"}}

            User: Hey what's up?
            Output: {{"request": "UNKNOWN"}}

            User: Write me a function that adds two numbers.
            Output: {{"request": "PYTHON", "code": "def add(a, b): return a + b"}}

            User: Play the song luther
            Output: {{"request": "MUSIC-PLAY", "songname": "luther", "artistname": "unknown"}}

            User: Do I have anything in my mail?
            Output: {{"request": "NOTIFICATION-GMAIL"}}

            
        """

        self.__history = [{
            "role": "system",
            "content": self.__system_message
        }]
        self.__model_name = model_name
    
    def get_classification(self, query):
        print(self.curr_day)
        self.__history.append({"role": "user", "content": query})
        ollama_host = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
        os.environ["OLLAMA_HOST"] = ollama_host
        try:
            response = ollama.chat(
                        model=self.__model_name,
                        messages= [self.history[0], self.history[-1]])
            if not "message" in response or not "content" in response["message"]:
                raise ValueError("Returned chat object failed to provide message and/or content.")
            jsonRes = json.loads(response["message"]["content"])
            return jsonRes
        except Exception as e:
            print(f"CLASSIFICATION ERROR: {e}")
            return json.loads('{"request": "UNKNOWN"}')
    
    

    @property
    def history(self):
        return self.__history
    
    @property
    def model_name(self):
        return self.__model_name
    
    @property
    def curr_day(self):
        return date.today()