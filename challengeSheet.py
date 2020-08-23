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
from kovaak.challenges import Challenge
import logging
import hashlib
from myG.gservice import gService
import myG.gsheet

logging.basicConfig(level=logging.ERROR)
logging.propagate = False

# ChallengeSheet child for creating and editing sheets based on challenge data
class ChallengeSheet(myG.gsheet.gSheet):
    def __init__(self, service, driveService, title:str, challenges:Dict):
        super().__init__(service, driveService, title)
        self.__challenges = challenges
        self.__spreadsheetRequests =[]
        self.__valueRequests=[]
    
    def getChallengeDict(self) :
        return self.__challenges

    # used to get the sheetId from the title
    def myHash(self, string:str)->int:
        return int( hashlib.sha1( string.encode('utf-8') ).hexdigest(),base=16 ) % (10**8) #generate sheetId by hashing title
    
    def removeFirstSheet(self):
        self.__spreadsheetRequests.append({
            "deleteSheet":{
                'sheetId': 0
            }
        })

    def sendRequests(self):
        #send spreadsheet requests
        if len(self.__spreadsheetRequests) > 0 :
            body = {
                'requests' : self.__spreadsheetRequests
            }
            logging.info('sending spreadsheet batch update:\n', body)
            response = self._service.spreadsheets().batchUpdate(spreadsheetId=self._ID, body=body).execute()
            print(response)
            self.__spreadsheetRequests=[] #reset requests list after sending API call
        #send value update requests
        if len(self.__valueRequests) > 0 :
            body={
                'valueInputOption': 'USER_ENTERED',
                'data':self.__valueRequests
            }
            logging.info('sending value batch update:\n', body)
            response = self._service.spreadsheets().values().batchUpdate(spreadsheetId=self._ID, body=body).execute()
            print(response)
            self.__valueRequests=[]

    def updateValues(self, title:str, challenges:List[Challenge]):
        values = []
        for challenge in challenges : 
            values.append([
                challenge.get('date')+'-'+challenge.get('time'),
                challenge.get('name'),
                challenge.get('score'),
                challenge.get('accuracy'),
                challenge.get('sens'),
                challenge.get('sensGame')
            ])

        body = {'values': values}

        result = self._service.spreadsheets().values().append( spreadsheetId=self._ID ,
                                                            range=title,
                                                            valueInputOption='USER_ENTERED',
                                                            body=body).execute()
        print(result)
    
    def sortValues(self, sheetTitle:str):
        sheetId = self.myHash(sheetTitle)        
        self.__spreadsheetRequests.append({
            "sortRange":{
                'range':{
                    'sheetId': sheetId,
                    'startRowIndex': 0,
                    'startColumnIndex':0,
                    'endColumnIndex': 1
                },
                'sortSpecs': [
                    {
                        'sortOrder': 'ASCENDING',
                    }
                ]
            }
        })

    # this should take in a dictionary key value pair.
    # the key is the title while the value is a list of challenges
    def createSheet(self, sheetIndex:int, title:str, challenges:List[Challenge]):
        # hash the title to get the sheetId
        sheetId = self.myHash(title)
        
        #check if the sheet already exists
        sheetMetadata = self._service.spreadsheets().get(spreadsheetId=self._ID).execute()
        currentSheets = sheetMetadata.get('sheets', '')
        for s in currentSheets :
            checkTitle = s.get('properties',{}).get('title','no_title')
            checkID = s.get('properties',{}).get('sheetId','no_id')
            if checkTitle == title:
                if checkID == sheetId:
                    self.updateValues(title, challenges) #update values if sheet already exists
                    return #exit function if sheet already exists

        # generate the cell values
        values = [['Date-Time', 'Challenge', 'Score', 'Accuracy', 'Sensitivity', 'Game Sens']]

        for challenge in challenges :
            values.append([
                challenge.get('date')+'-'+challenge.get('time'),
                challenge.get('name'),
                challenge.get('score'),
                challenge.get('accuracy'),
                challenge.get('sens'),
                challenge.get('sensGame')
            ])

        # add the value data to the table
        self.__valueRequests.append({
            'range': title,
            'majorDimension': 'ROWS',
            'values' : values
        })

        #number of columns from left to anchor the chart
        chartOffset = len(values[0])
        #create the sheet
        self.__spreadsheetRequests.append({
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
        self.__spreadsheetRequests.append({
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
                                'columnIndex': chartOffset
                            },
                            'widthPixels': 800,
                        }
                    }

                }
            }
        })

        #make a score chart
        self.__spreadsheetRequests.append({
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
                                'columnIndex': chartOffset
                            },
                            'widthPixels': 800,
                        }
                    }

                }
            }
        })

        #make accuracy chart
        self.__spreadsheetRequests.append({
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
                                'columnIndex': chartOffset
                            },
                            'widthPixels': 800,
                        }
                    }

                }
            }
        })


        
