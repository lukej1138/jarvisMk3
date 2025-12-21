from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
from dotenv import load_dotenv

load_dotenv()

class GoogleTokenManager:
    def __init__(self):
        #Note: Potentially make this a publisher-subscriber design where calendarGoogle and gmailGoogle add their own scopes; for now good enough
        self.SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/gmail.readonly"]
        if os.path.exists(os.getenv("GOOGLE_TOKEN_PATH")):
            self.creds = Credentials.from_authorized_user_file(os.getenv("GOOGLE_TOKEN_PATH"), self.SCOPES)
        else: 
            self.creds = None
    
    def buildCreds(self):
        if self.creds:
            return 
        try:
            flow = InstalledAppFlow.from_client_secrets_file(os.getenv("GOOGLE_SECRET_PATH"), self.SCOPES)
            self.creds = flow.run_local_server(port=8080, access_type = "offline", prompt = "consent", success_message="Successfully downloaded credentials. This window can be closed.")
            with open(os.getenv("GOOGLE_TOKEN_PATH"), "w") as file:
                file.write(self.creds.to_json())
            return self.creds
        except Exception as e:
            print(e)
            return None

    # If creds DNE, 
    def refreshCreds(self):
        if not self.creds or not self.creds.refresh:
            return self.buildCreds()
        elif self.creds.expired and self.creds.refresh:
            self.creds.refresh(Request())
            with open(os.getenv("GOOGLE_TOKEN_PATH"), "w") as file:
                file.write(self.creds.to_json())
        return self.creds
    
    def getCreds(self):
        return self.refreshCreds()
    