import csv
from sys import platform
import os
from typing import Dict, List, Set

class Challenge :
    def __init__(self, filePath, name, date, time) :
        self.filePath = filePath
        self.name = name
        self.date = date
        self.time = time

        self.score = 0
        self.accuracy = 0
        self.sensGame = "empty"
        self.sens = 0
        self.initStats()
        # print("")
        # self.printVars()

    def initStats(self):
        with open(self.filePath, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            prevRow = ''
            for row in reader:
                if len(row) : #check if row exists
                    if row[0] == 'Score:' : #look for the score row
                        self.score = row[1]
                    if len(prevRow): #check the previous row for the shots/hits categories
                        if prevRow[0] == 'Weapon' :
                            try:
                                self.accuracy = round(float(row[2]) / float(row [1]),5)
                            except:
                                self.accuracy = "undefined"
                    if row[0] == 'Sens Scale:' :
                        self.sensGame = row[1]
                    if row[0] == 'Horiz Sens:' :
                        self.sens = row[1]
                prevRow = row #update previous row

    def printVars(self):
        print('filePath: ',self.filePath)
        print('name: ',self.name)
        print('date: ',self.date)
        print('time: ',self.time)
        print('score: ', self.score)
        print('accuracy: ', self.accuracy)
        print('sens (game): ', self.sensGame)
        print('sens: ', self.sens)

class Challenges:
    def __init__(self, directory, title:str="allData", playlist:Set={}):
        self.__title = title
        self.__data = self.initChallenges(directory, playlist)
    def getData(self):
        return self.__data
    # User has option to specify playlist, if no playlist is specified, all data will be loaded
    def initChallenges(self, directory:str, playlist:Set={})->Dict[str, List[Challenge]]:
        #create an empty dictionary to store challenges in
        challenges = {}
        checkedData = [] #list to record file names of checked data
        for filename in os.listdir(directory):
            if filename.endswith(".csv") :
                #trim ' Stats.csv' suffix
                #split pieces of the name by the delimiter
                namePieces = filename[0:-10].split(' - ')
                namePieces[0] = namePieces[0].lstrip()#remove forward spaces
                namePieces[0] = namePieces[0].rstrip() #remove trailing spaces

                if (len(playlist)==0) or (namePieces[0] in playlist):

                    #split the time based on the delimiter
                    timePieces = namePieces[-1].split('-')
                    timePieces[0] = timePieces[0].replace('.', '/')
                    timePieces[1] = timePieces[1].replace('.', ':')

                    challenge = Challenge(os.path.join(directory, filename), namePieces[0], timePieces[0], timePieces[1])

                    if namePieces[0] not in challenges :
                        challenges[namePieces[0]] = []
                    challenges[namePieces[0]].append(challenge)
                    checkedData.append(filename) #record file names of checked data
            else:
                continue
        #record that the challenge data has been processed into a local csv
        #this is important for updating tables later
        with open(f"data/{self.__title}-checkedData.csv", 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for data in checkedData :
                writer.writerow([data])

        return challenges

    # def checkNew(self):



if __name__ == "__main__" :
    #change path based on OS; maybe put this into args later

    if platform == "linux" or platform =="linux2":
        statsDir = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
    elif platform == "win32":
        statsDir = 'C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats'

    ch = Challenges(directory=statsDir)
    
    data = ch.getData()

    for key in data:
        print(f"key: {key}")
        print("values: ")
        for v in data[key]:
            v.printVars()
