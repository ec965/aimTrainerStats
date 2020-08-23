import re
import string
import os
from typing import OrderedDict, List

# current errors:
# )% as leading chars
# ( as leading char
# %! as leading char

#use this to look for irregularities
def findIrregular( s:str):
    if not (s[0].isalpha() or s[0].isdigit()):
        print('IRREGULAR NAME FOUND')
        print(s)
        print('END IRREGULAR NAME')

def findMatchingBracket(s:str)->bool:
    pstack = []

    for c in s :
        if c=="(" :
            pstack.append(c)
        elif c == ")" :
            if len(pstack) == 0 :
                return False
            pstack.pop()
    if len(pstack) == 0:
        return True
    return False

#generates a dictionary of {title:challenges} for each playlist
def getPlaylists(directory:str)->OrderedDict[str, List[str]]:
    playlist = {}
    for file in os.listdir(directory):
        with open(f"{directory}/{file}",'r', errors='ignore') as file:
            data = file.read()
            #remove all non alphanumeric characters
            regex = re.compile('[^a-zA-Z0-9\!\$\%\^\&\*\(\)\-\_\=\+ ]')
            data = regex.sub('', data)
            #split at delimiter
            delimiter = 'Property'
            data = data.split(delimiter)
            #remove unnessesary strings
            for i in range(0, len(data)):
                data[i] = data[i].replace('PlayCountInt','').replace('ScenarioListArray','')
                # print(f"{i}\t{data[i]}")
            #write data into playlist dictionary
            playlist[data[2]] = []
            for i in range( 6, len(data)):
                if i%2 == 0:
                    challenge = data[i].strip()
                    
                    # fix irregularities
                    if challenge[0:2] == ')%' :
                        challenge = challenge[2:]
                    elif challenge[0:2] == '%!' :
                        challenge = challenge[2:]
                    elif challenge[0] == '(' :
                        if not findMatchingBracket(challenge) :
                            challenge = challenge[1:]
                    
                    findIrregular(challenge)

                    playlist[data[2]].append(challenge)
    return playlist


if __name__ == "__main__" :
    directory = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/Saved/SaveGames/Playlists'

    playlists = getPlaylists(directory)

    for i in playlists :
        print(f"playlist name: {i}")
        print(playlists[i])
