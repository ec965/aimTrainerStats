from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from gservice import gService
import logging
from gservice import gService
import csv
logging.basicConfig(level=logging.ERROR)

#use this class to find a file or folder in your google drive
class gFind:
    #service should be google drive service
    def __init__(self, service):
        self.service = service

    def findFile(self, fileName:str, fileID:str)->bool:
        page_token = None
        nameQuery = "name = '" + fileName + "'"
        while True:
            response = self.service.files().list(q=nameQuery,
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

class gFolder(gFind):
    # service should be the google drive service
    def __init__(self, service, folderName):
        super().__init__(service)
        self.service = service
        self.folderName = folderName
        self.ID = self.getID(folderName)

    def createFolder(self, folderName:str)->str:
        print('creating a new folder named:', folderName)
        file_metadata = {
            'name' : folderName,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        file = self.service.files().create(body=file_metadata, fields='id').execute()
        print(file)

        ID = file.get('id')
        #write foldername and ID to csv
        with open('gdrivedata.csv','a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([self.folderName, ID])

        return ID

    def getID(self, folderName:str)->str :
        #check if there is folder data in the local csv
        print('looking for exisiting G-drive folder')

        #check if csv data file exists
        if os.path.exists('gdrivedata.csv'):
            with open('gdrivedata.csv', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    if row[0] == folderName :
                        print('exisiting folder found')
                        return row[1]
            print('no folderID in G-drive found')

        return self.createFolder(self.folderName)

    def moveFileHere( self, fileID:str ):
        print('moving file: ', fileID)
        # get exisiting parents (file path) to remove
        file = self.service.files().get(fileId=fileID, fields='parents').execute()
        previousParents = ','.join(file.get('parents'))
        # move file to new folder
        file = self.service.files().update(fileId=fileID,
                                           addParents=self.ID,
                                           removeParents=previousParents,
                                           fields='id, parents').execute()


if __name__ == "__main__" :
    service = gService()
    folder = gFolder(service.drive, 'test1')
    finder = gFind(service.drive)

    print(finder.findFile('test1',folder.ID))
