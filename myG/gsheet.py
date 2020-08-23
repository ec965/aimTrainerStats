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
import logging
import hashlib
from myG.gservice import gService
import myG.gdrive

logging.basicConfig(level=logging.ERROR)
logging.propagate = False

#give the app read and write privilege

class gSheet:
    def __init__(self, service, driveService, title:str):
        self.__csvName = 'data/gdrivedata.csv'
        self.__title = title
        self._service = service #service that has the auth keys etc.
        self._ID = self.initID(driveService) #spreadsheetId
    
    def get(self, s:str):
        if s=='ID':
            return self._ID
        elif s=='title':
            return self.__title

    def createNewSpreadsheet(self, title:str)->str:
        print('creating a new spreadsheet')
        #create a new spreadsheet
        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self._service.spreadsheets().create(body=spreadsheet,
                                                    fields='spreadsheetId').execute()
        print(spreadsheet)
        ID = spreadsheet.get('spreadsheetId')
        #write the title and spread sheet ID to csv
        with open(self.__csvName, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow([self.__title, ID])

        return ID

    def initID(self, driveService)->str:
        #check if there is spreadsheet information on file
        print('looking for exisitng G-drive spreadsheet')
        if os.path.exists(self.__csvName):
            with open(self.__csvName, newline='') as csvfile:
                reader = csv.reader(csvfile,delimiter=',')
                for row in reader:
                    if row[0] == self.__title :
                        print('exisitng local spreadsheet data found')
                        ID = row[1]

                        #check the google drive to verify if the spread sheet exists on the remote location
                        if myG.gdrive.findFile(driveService, self.__title, ID):
                            print('existing G-drive spreadsheet found')
                            return ID
        #else create a new spreadsheet
        print('no spreadsheet in G-drive found')
        return self.createNewSpreadsheet(self.__title)

if __name__ == '__main__':
    googleService = gService()
    sheet = gSheet('FPS Aim Trainer Stats', googleService.sheet)
