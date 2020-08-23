from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Dict

import logging
logging.getLogger('googleapicliet.discovery_cache').setLevel(logging.ERROR)

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']

class gService:
    def __init__(self):
        services = self.createLogin()
        self.__sheet = services['sheet']
        self.__drive = services['drive']

    def get(self,string:str):
        if (string == 'sheet'):
            return self.__sheet
        if (string == 'drive'):
            return self.__drive
        else :
            return False

    def createLogin(self)->Dict:
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        sheet = build('sheets', 'v4', credentials=creds, cache_discovery=False)
        drive = build('drive', 'v3', credentials=creds, cache_discovery=False)
        services = {'sheet':sheet, 'drive':drive}
        return services

if __name__ == "__main__":
    gs = gService()
    spid='1V4D9epPWfQAAJGzUSkrR4L4O-4Y_dUQYFKMJkdDDWwM'
    shmetadata = gs.get('sheet').spreadsheets().get(spreadsheetId=spid).execute()
    sheets = shmetadata.get('sheets', '')
    for s in sheets : 
        title = s.get('properties', {}).get('title','no_title')
        sheetid = s.get('properties',{}).get('sheetId','no_id')
        print (f"{title}\t{sheetid}")
        print('\n')
