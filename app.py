import challenges as Ch
import gsheet
from sys import platform

def main ():
    #change path based on OS; maybe put this into args later
    if platform == "linux" or platform =="linux2":
        statsDir = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
    elif platform == "win32":
        statsDir = 'C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats'

    ch = Ch.Challenges(statsDir)

    for key, value in ch.challengeDict.items():
        print(key, '\n', len(value))

