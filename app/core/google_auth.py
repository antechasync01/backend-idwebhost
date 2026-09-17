import os
from typing import List
from google_auth_oauthlib.flow import InstalledAppFlow

def auth_google(scopes: List[str]=["https://www.googleapis.com/auth/calendar.readonly"], json_client:str | None = None ):

    # Resolve path relative to this file's directory
    if json_client == None:
        raise Exception("Google Client JSON file is required")
        
    _DIR = os.path.dirname(os.path.abspath(__file__))
    _CLIENT_SECRET = os.path.join(
        _DIR,
        json_client
    )

    flow = InstalledAppFlow.from_client_secrets_file(
        _CLIENT_SECRET,
        scopes
    )

    credentials = flow.run_local_server(
        port=8090,
        access_type="offline",
        prompt="consent"
    )

    print("ACCESS TOKEN:")
    print(credentials.token)

    print("\nREFRESH TOKEN:")
    print(credentials.refresh_token)

if __name__ == "__main__":
    auth_google()