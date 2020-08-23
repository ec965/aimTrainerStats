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
                        if myG.gdrive.findFile(driveService, self.title, ID):
                            print('existing G-drive spreadsheet found')
                            return ID
        #else create a new spreadsheet
        print('no spreadsheet in G-drive found')
        return self.createNewSpreadsheet(self.title)

if __name__ == '__main__':
    googleService = gService()
    sheet = gSheet('FPS Aim Trainer Stats', googleService.sheet)
