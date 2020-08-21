from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
from typing import Dict, List
from challenges import Challenge
import logging
import hashlib

logging.basicConfig(level=logging.WARNING)
logging.propagate = True

#give the app read and write privilege
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class gSheet:
    def __init__(self, title:str):
        self.title = title
        self.service = self.createLogin()
        self.ID = self.getID()

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
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId').execute()

        ID = spreadsheet.get('spreadsheetId')
        #write the spread sheet ID to JSON
        sheetJSON = {"ID": ID}
        with open('spreadsheet.json', 'w') as json_file:
            json.dump(sheetJSON, json_file)

        return ID

    def getID(self)->str:
        #check if the spread sheet exists...
        if os.path.exists('spreadsheet.json') :
            with open('spreadsheet.json') as file:
                data = json.load(file)
            if data['ID'] :
                return data['ID']
        #else create a new spreadsheet
        return self.createNewSpreadsheet(self.title)

# ChallengeSheet child for creating and editing sheets based on challenge data
class ChallengeSheet(gSheet):
    def __init__(self, title:str, challenges:Dict):
        super().__init__(title)
        self.challenges = challenges
        self.spreadsheetRequests =[]
        self.valueRequests=[]

    # used to get the sheetId from the title
    def myHash(self, string:str)->int:
        return int( hashlib.sha1( string.encode('utf-8') ).hexdigest(),base=16 ) % (10**8) #generate sheetId by hashing title
    
    def sendRequests(self):
        #send spreadsheet requests
        if len(self.spreadsheetRequests) > 0 :
            body = {
                'requests' : self.spreadsheetRequests
            }
            logging.warning('sending spreadsheet batch update:\n')
            logging.warning(body)
            response = self.service.spreadsheets().batchUpdate(spreadsheetId=self.ID, body=body).execute()
            print(response)
            self.spreadsheetRequests=[] #reset requests list after sending API call
        
        #send value update requests
        if len(self.valueRequests) > 0 :
            body={
                'valueInputOption': 'USER_ENTERED', 
                'data':self.valueRequests
            }
            logging.warning('sending value batch update:\n')
            logging.warning(body)
            response = self.service.spreadsheets().values().batchUpdate(spreadsheetId=self.ID, body=body).execute()
            print(response)
            self.valueRequests=[]

    # this should take in a dictionary key value pair.
    # the key is the title while the value is a list of challenges
    def createSheet(self, sheetIndex:int, title:str, challenges:List[Challenge]): 
        # hash the title to get the sheetId
        sheetId = self.myHash(title)
        logging.warning('sheetId')
        logging.warning(sheetId)
        
        # generate the cell values
        values = [['Date/Time', 'Challenge', 'Score', 'Accuracy', 'Sensitivity', 'Game Sens']]

        for challenge in challenges :
            values.append([
                challenge.date+' '+challenge.time,
                challenge.name,
                challenge.score,
                challenge.accuracy,
                challenge.sens,
                challenge.sensGame
            ])

        #create the sheet
        self.spreadsheetRequests.append({
            'addSheet' : {
                'properties': {
                    "sheetId" : sheetId,
                    "title": title,
                    "index": sheetIndex,
                    "sheetType" : "GRID",
                    'hidden': False
                }
            }
        })
            
        #make a chart
        self.spreadsheetRequests.append({
            'addChart':{
                'chart':{
                    'chartId': 0,
                    'spec': {
                        'title': title,
                        'basicChart': {
                            'chartType': 'LINE',
                            'domains': [
                                {
                                    'domain':{
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    title+'!A1:A'
                                                }
                                            ]
                                        }
                                    }
                                }
                            ],
                            'series': [
                                {
                                    'series': {
                                        'sourceRange' : {
                                            'sources':{
                                                title+'!D1:D'
                                            }
                                        }
                                    }
                                },
                                {
                                    'series': {
                                        'sourceRange' : {
                                            'sources':{
                                                title+'!C1:C'
                                            }
                                        }
                                    }
                                }
                            ]
                        }
                    },
                    "position": {
                        'sheetId': sheetId,
                        'overlayPosition' :{
                            'anchorCell':{
                                'sheetId': sheetId,
                                'rowIndex': 0,
                                'columnIndex': len(values[0])
                            }
                        }
                    }

                }
            }
        })

        # add the value data to the table
        self.valueRequests.append({
            'range': title,
            'majorDimension': 'ROWS',
            'values' : values
        })






if __name__ == '__main__':
    sheet = gSheet('FPS Aim Trainer Stats')
