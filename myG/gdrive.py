from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from myG.gservice import gService
import logging
import csv
logging.basicConfig(level=logging.ERROR)


def findFile(driveService, fileName:str, fileID:str)->bool:
    page_token = None
    nameQuery = f"name = '{fileName}'"
    while True:
        response = driveService.files().list(q=nameQuery,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
        for file in response.get('files', []):
            print( 'Found file\tname: ', file.get('name'), '\tid: ', file.get('id') )
            if fileID == file.get('id'):
                return True
        token = response.get('nextPageToken', None)
        if page_token is None:
            return False

class gFolder:
    # service should be the google drive service
    def __init__(self, service, folderName):
        self.__csvName = 'data/gdrivedata.csv'
        self.__service = service
        self.__folderName = folderName
        self.__ID = self.initID(folderName)
    
    def get(self, s:str):
        if(s=='ID'):
            return self.__ID
        elif(s=='folderName'):
            return self.__folderName

    def createFolder(self, folderName:str)->str:
        print('creating a new folder named:', folderName)
        file_metadata = {
            'name' : folderName,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        file = self.__service.files().create(body=file_metadata, fields='id').execute()
        print(file)

        ID = file.get('id')
        #write foldername and ID to csv
        with open(self.__csvName,'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([self.__folderName, ID])

        return ID

    def initID(self, folderName:str)->str :
        #check if there is folder data in the local csv
        print('looking for exisiting G-drive folder')

        #check if csv data file exists
        if os.path.exists(self.__csvName):
            with open(self.__csvName, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    if row[0] == self.__folderName :
                        print('exisiting local folder data found')
                        ID = row[1]

                        #check google drive to verify that folder exists
                        if findFile(self.__service, folderName, ID) :
                            print('existing G-drive folder found')
                            return ID

        print('no folderID in G-drive found')
        return self.createFolder(self.__folderName)

    def moveFileHere( self, fileID:str ):
        print('moving file: ', fileID)
        # get exisiting parents (file path) to remove
        file = self.__service.files().get(fileId=fileID, fields='parents').execute()
        previousParents = ','.join(file.get('parents'))
        # move file to new folder
        file = self.__service.files().update(fileId=fileID,
                                           addParents=self.__ID,
                                           removeParents=previousParents,
                                           fields='id, parents').execute()


if __name__ == "__main__" :
    service = gService()
    folder = gFolder(service.drive, 'test1')

    print(findFile('test1',folder.ID))
