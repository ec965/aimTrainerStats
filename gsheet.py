from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

#give the app read and write privilege
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class gSheet:
    def __init__(self, title):
        self.__title = title
        self.__service = self.createLogin()
        self.__ID = self.getID()

    def createLogin(self):
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

        return build('sheets', 'v4', credentials=creds)

    def createNewSpreadsheet(self, title:str)->str:
        #create a new spreadsheet
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.__service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId').execute()

        ID = spreadsheet.get('spreadsheetId')
        #write the spread sheet ID to JSON
        sheetJSON = {"ID": ID}
        with open('spreadsheet.json', 'w') as json_file:
            json.dump(sheetJSON, json_file)

        return ID

    def getID(self)->str:
        if os.path.exists('spreadsheet.json') :
            with open('spreadsheet.json') as file:
                data = json.load(file)
            if data['ID'] :
                return data['ID']

        return self.createNewSpreadsheet(self.__title)

    def createSheet():



if __name__ == '__main__':
    sheet = gSheet('FPS Aim Trainer Stats')
