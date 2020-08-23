import csv
from sys import platform
import os
from typing import Dict, List, Set

class Challenge :
    def __init__(self, filePath, name, date, time) :
        self.__filePath = filePath
        self.__name = name
        self.__date = date
        self.__time = time

        self.__score = 0
        self.__accuracy = 0
        self.__sensGame = "empty"
        self.__sens = 0
        self.initStats()
        # print("")
        # self.printVars()
    def get(self, s:str):
        if s=='name':
            return self.__name
        elif s=='date':
            return self.__date
        elif s=='time':
            return self.__time
        elif s=='score':
            return self.__score
        elif s=='accuracy':
            return self.__accuracy
        elif s=='sensGame':
            return self.__sensGame
        elif s=='sens':
            return self.__sens
        elif s=='filePath':
            return self.__filePath

    def initStats(self):
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
    def __init__(self, directory, title:str="allData", playlist:Set={}):
        self.__title = title
        self.__data = self.initChallenges(directory, playlist)
    def getData(self):
        return self.__data
    # User has option to specify playlist, if no playlist is specified, all data will be loaded
    def initChallenges(self, directory:str, playlist:Set={})->Dict[str, List[Challenge]]:
        #create an empty dictionary to store challenges in
        challenges = {}

        #use a Set to load file names of checked data
        checkedData = set([])
        if os.path.exists(f"data/{self.__title}-checkedData.csv") :
            with open(f"data/{self.__title}-checkedData.csv", newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for row in reader:
                    checkedData.add(row[0])
        
        #use a set to record names of new data
        newData = set([])
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                if (filename not in checkedData) :
                    #trim ' Stats.csv' suffix
                    #split pieces of the name by the delimiter
                    namePieces = filename[0:-10].split(' - ')
                    namePieces[0] = namePieces[0].lstrip()#remove forward spaces
                    namePieces[0] = namePieces[0].rstrip() #remove trailing spaces

                    if (len(playlist)==0) or (namePieces[0] in playlist):
                        print('processing: ',filename)
                        #split the time based on the delimiter
                        timePieces = namePieces[-1].split('-')
                        timePieces[0] = timePieces[0].replace('.', '/')
                        timePieces[1] = timePieces[1].replace('.', ':')

                        challenge = Challenge(os.path.join(directory, filename), namePieces[0], timePieces[0], timePieces[1])

                        if namePieces[0] not in challenges :
                            challenges[namePieces[0]] = []
                        challenges[namePieces[0]].append(challenge)
                        newData.add(filename) #record file names of checked data
            else:
                continue
        #record that the challenge data has been processed into a local csv
        #this is important for updating tables later
        with open(f"data/{self.__title}-checkedData.csv", 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for data in newData :
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
