import challenges as Ch
from gsheet import ChallengeSheet
from sys import platform
import logging

logging.basicConfig(level=logging.WARNING)
logging.propagate = False
# user inputs:
# steam library path
# Kovaak playlist
# Spreadsheet title

def main ():
    #use an arg for the steam library path
    # steamLibPath = 'C:/Program Files (x86)/Steam'
    #change path based on OS; maybe put this into args later
    logging.warning('current OS: ', platform)
    if platform == "linux" or platform =="linux2":
        steamLib = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
    elif platform == "win32":
        steamLib = 'C:/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'

    playLists = {
        'Flicks' : ['Tile Frenzy', 'Tile Frenzy Mini', '1wall6targets TE', '1wall 6targets small', 'Valorant Microshot Speed Small 60s', 'Valorant Reflex Flick'],
        'Tracking': ['patTargetSwitch', 'Midrange Long Strafes Invincible', 'Cata IC Long Strafes', 'Cata IC Fast Strafes', '1wall5targets_pasu', 'patTargetSwitch V2']
    }
    
    for title, playlist in playLists.items() :
        kovaakData = Ch.Challenges(steamLib, playlist)
        kovaakGoogleSheet = ChallengeSheet(title, kovaakData.data)

        for index, (key, value) in enumerate(kovaakGoogleSheet.challenges.items()):
            logging.warning('key: ', key)
            logging.warning('value', value)
            kovaakGoogleSheet.createSheet(index, key, value)

        kovaakGoogleSheet.sendRequests()

if __name__=="__main__":
    main()

