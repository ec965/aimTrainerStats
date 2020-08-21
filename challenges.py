import csv
from sys import platform
import os
from typing import Dict, List

class Challenge :
    def __init__(self, filePath, name, date, time) :
        self.__filePath = filePath
        self.__name = name
        self.__date = date
        self.__time = time

        self.__score = 0
        self.__accuracy = 0
        self.__sensGame = ""
        self.__sens = 0
        self.getStats()
        # print("")
        # self.printVars()

    def getStats(self):
        with open(self.__filePath, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            prevRow = ''
            for row in reader:
                if len(row) : #check if row exists
                    if row[0] == 'Score:' : #look for the score row
                        self.__score = row[1]
                    if len(prevRow): #check the previous row for the shots/hits categories
                        if prevRow[0] == 'Weapon' :
                            try:
                                self.__accuracy = round(float(row[2]) / float(row [1]),5)
                            except:
                                self.__accuracy = "undefined"
                    if row[0] == 'Sens Scale:' :
                        self.__sensGame = row[1]
                    if row[0] == 'Horiz Sens:' :
                        self.__sens = row[1]
                prevRow = row #update previous row

    def printVars(self):
        print('filePath: ',self.__filePath)
        print('name: ',self.__name)
        print('date: ',self.__date)
        print('time: ',self.__time)
        print('score: ', self.__score)
        print('accuracy: ', self.__accuracy)
        print('sens (game): ', self.__sensGame)
        print('sens: ', self.__sens)

class Challenges:
    def __init__(self, directory):
        self.directory = directory
        self.challengeDict = self.getChallenges(self.directory)
    def getChallenges(self, directory:str)->Dict[str, List[Challenge]]:
        challenges = {}
        for filename in os.listdir(directory):
            if filename.endswith(".csv") :
                #trim ' Stats.csv' suffix
                #split pieces of the name by the delimiter
                namePieces = filename[0:-10].split(' - ')
                #split the time based on the delimiter
                timePieces = namePieces[-1].split('-')

                challenge = Challenge(os.path.join(directory, filename), namePieces[0], timePieces[0], timePieces[1])

                if namePieces[0] not in challenges :
                    challenges[namePieces[0]] = []
                challenges[namePieces[0]].append(challenge)
            else:
                continue
        return challenges

    def checkNew(self):



if __name__ == "__main__" :
    #change path based on OS; maybe put this into args later
    if platform == "linux" or platform =="linux2":
        statsDir = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
    elif platform == "win32":
        statsDir = 'C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats'
    
    ch = Challenges(statsDir)

    for key, value in ch.challengeDict.items():
        print(key, '\n', len(value))
