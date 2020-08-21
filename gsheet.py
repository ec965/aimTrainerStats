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
logging.propagate = False

#give the app read and write privilege
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

class gSheet:
    def __init__(self, title:str, service):
        self.title = title
        self.service = service #service that has the auth keys etc.
        self.ID = self.getID() #spreadsheetId

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
        # sheetJSON = {"ID": ID}
        # with open('spreadsheet.json', 'w') as json_file:
        #     json.dump(sheetJSON, json_file)

        return ID

    def getID(self)->str:
        #check if the spread sheet exists...
        # if os.path.exists('spreadsheet.json') :
        #     with open('spreadsheet.json') as file:
        #         data = json.load(file)
        #     if data['ID'] :
        #         return data['ID']
        #else create a new spreadsheet
        return self.createNewSpreadsheet(self.title)

# ChallengeSheet child for creating and editing sheets based on challenge data
class ChallengeSheet(gSheet):
    def __init__(self, service, title:str, challenges:Dict):
        super().__init__(title, service)
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

        # generate the cell values
        values = [['Date-Time', 'Challenge', 'Score', 'Accuracy', 'Sensitivity', 'Game Sens']]

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

        #make a score chart
        self.spreadsheetRequests.append({
            'addChart':{
                'chart':{
                    'chartId': sheetId+1,
                    'spec': {
                        'title': title+' Score',
                        'basicChart': {
                            'chartType': 'LINE',
                            'axis': [
                                {
                                    'position': 'BOTTOM_AXIS',
                                    'title': 'Date/Time',
                                },
                                {
                                    'position': 'LEFT_AXIS',
                                    'title': 'Score'
                                }
                            ],
                            'domains': [
                                {
                                    'domain':{
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': sheetId,
                                                    'startRowIndex': 1,
                                                    'startColumnIndex':0,
                                                    'endColumnIndex':1
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
                                                'sheetId': sheetId,
                                                'startRowIndex': 1,
                                                'startColumnIndex':2,
                                                'endColumnIndex':3
                                            }
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                }
                            ]
                        }
                    },
                    "position": {
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

        #make accuracy chart
        self.spreadsheetRequests.append({
            'addChart':{
                'chart':{
                    'chartId': sheetId+2,
                    'spec': {
                        'title': title+' Accuracy',
                        'basicChart': {
                            'chartType': 'LINE',
                            'axis': [
                                {
                                    'position': 'BOTTOM_AXIS',
                                    'title': 'Date/Time',
                                },
                                {
                                    'position': 'LEFT_AXIS',
                                    'title': 'Accuracy'
                                }
                            ],
                            'domains': [
                                {
                                    'domain':{
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': sheetId,
                                                    'startRowIndex': 1,
                                                    'startColumnIndex':0,
                                                    'endColumnIndex':1
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
                                                'sheetId': sheetId,
                                                'startRowIndex': 1,
                                                'startColumnIndex':3,
                                                'endColumnIndex':4
                                            }
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                }
                            ]
                        }
                    },
                    "position": {
                        'overlayPosition' :{
                            'anchorCell':{
                                'sheetId': sheetId,
                                'rowIndex': 20,
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
