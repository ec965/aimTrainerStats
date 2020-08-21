import challenges as Ch
from gsheet import ChallengeSheet
from sys import platform
import logging

logging.basicConfig(level=logging.WARNING)
logging.propagate = True

def main ():
    #use an arg for the steam library path
    # steamLibPath = 'C:/Program Files (x86)/Steam'
    #change path based on OS; maybe put this into args later

    logging.warning('current OS: ', platform)
    if platform == "linux" or platform =="linux2":
        steamLib = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
    elif platform == "win32":
        steamLib = 'C:/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'

    kovaakData = Ch.Challenges(steamLib)
    

    kovaakGoogleSheet = ChallengeSheet('FPS Aim Trainer Stats', kovaakData.challengeDict)

    for index, (key, value) in enumerate(kovaakGoogleSheet.challenges.items()):
        logging.warning('key: ', key)
        logging.warning('value', value)
        kovaakGoogleSheet.createSheet(index+1, key, value)
        break

    kovaakGoogleSheet.sendRequests()

if __name__=="__main__":
    main()

