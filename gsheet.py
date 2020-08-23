# Google API
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#
import csv
from typing import Dict, List
from challenges import Challenge
import logging
import hashlib
from gservice import gService
import gdrive

logging.basicConfig(level=logging.ERROR)
logging.propagate = False

#give the app read and write privilege

class gSheet:
    def __init__(self, service, driveService, title:str):
        self.csvName = 'data/gdrivedata.csv'
        self.title = title
        self.service = service #service that has the auth keys etc.
        self.ID = self.getID(driveService) #spreadsheetId

    def createNewSpreadsheet(self, title:str)->str:
        print('creating a new spreadsheet')
        #create a new spreadsheet
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId').execute()
        print(spreadsheet)
        ID = spreadsheet.get('spreadsheetId')
        #write the title and spread sheet ID to csv
        with open(self.csvName, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow([self.title, ID])

        return ID

    def getID(self, driveService)->str:
        #check if there is spreadsheet information on file
        print('looking for exisitng G-drive spreadsheet')
        if os.path.exists(self.csvName):
            with open(self.csvName, newline='') as csvfile:
                reader = csv.reader(csvfile,delimiter=',')
                for row in reader:
                    if row[0] == self.title :
                        print('exisitng local spreadsheet data found')
                        ID = row[1]

                        #check the google drive to verify if the spread sheet exists on the remote location
                        if gdrive.findFile(driveService, self.title, ID):
                            print('existing G-drive spreadsheet found')
                            return ID
        #else create a new spreadsheet
        print('no spreadsheet in G-drive found')
        return self.createNewSpreadsheet(self.title)

# ChallengeSheet child for creating and editing sheets based on challenge data
class ChallengeSheet(gSheet):
    def __init__(self, service, driveService, title:str, challenges:Dict):
        super().__init__(service, driveService, title)
        self.csvName = 'gdrivedata.csv'
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
            logging.info('sending spreadsheet batch update:\n', body)
            response = self.service.spreadsheets().batchUpdate(spreadsheetId=self.ID, body=body).execute()
            print(response)
            self.spreadsheetRequests=[] #reset requests list after sending API call
        #send value update requests
        if len(self.valueRequests) > 0 :
            body={
                'valueInputOption': 'USER_ENTERED',
                'data':self.valueRequests
            }
            logging.info('sending value batch update:\n', body)
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
                challenge.date+'-'+challenge.time,
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
        
        #make a combined chart
        self.spreadsheetRequests.append({
            'addChart':{
                'chart':{
                    'chartId': sheetId+3,
                    'spec': {
                        'title': title+' Score and Accuracy',
                        'basicChart': {
                            'chartType': 'LINE',
                            'legendPosition' : 'TOP_LEGEND',
                            'axis': [
                                {
                                    'position': 'BOTTOM_AXIS',
                                    'title': 'Date/Time',
                                },
                                {
                                    'position': 'LEFT_AXIS',
                                    'title': 'Score'
                                },
                                {
                                    'position': 'RIGHT_AXIS',
                                    'title': 'Accuracy',
                                    'viewWindowOptions': {
                                        'viewWindowMin': 0.0,
                                        'viewWindowMax': 1.0,
                                        'viewWindowMode': 'EXPLICIT'
                                    }
                                },
                            ],
                            'domains': [
                                {
                                    'domain':{
                                        'sourceRange': {
                                            'sources': [
                                                {
                                                    'sheetId': sheetId,
                                                    'startRowIndex': 0,
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
                                                'startRowIndex': 0,
                                                'startColumnIndex':2,
                                                'endColumnIndex':3
                                            }
                                        }
                                    },
                                    'targetAxis': 'LEFT_AXIS'
                                },
                                {
                                    'series': {
                                        'sourceRange' : {
                                            'sources':{
                                                'sheetId': sheetId,
                                                'startRowIndex': 0,
                                                'startColumnIndex':3,
                                                'endColumnIndex':4
                                            }
                                        }
                                    },
                                    'targetAxis': 'RIGHT_AXIS'
                                }
                            ],
                            'headerCount': 1
                        }
                    },
                    "position": {
                        'overlayPosition' :{
                            'anchorCell':{
                                'sheetId': sheetId,
                                'rowIndex': 40,
                                'columnIndex': len(values[0])
                            }
                        }
                    }

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

    
    # def updateSheet(self, sheetIndex:int, title:str, challenges:List[Challenge]):






if __name__ == '__main__':
    googleService = gService()
    sheet = gSheet('FPS Aim Trainer Stats', googleService.sheet)
