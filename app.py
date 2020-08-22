import challenges as Ch
from gsheet import ChallengeSheet
from sys import platform
import logging
from gservice import gService
from gdrive import gFolder, findFile

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

    folderName = 'FPS Aim Trainer Stats'
    # dictionary { str: {Set}}
    playLists = {
        'Flicks' : {'Tile Frenzy', 'Tile Frenzy Mini', '1wall6targets TE', '1wall 6targets small', 'Valorant Microshot Speed Small 60s', 'Valorant Reflex Flick'},
        'Tracking': {'patTargetSwitch', 'Midrange Long Strafes Invincible', 'Cata IC Long Strafes', 'Cata IC Fast Strafes', '1wall5targets_pasu', 'patTargetSwitch V2'}
    }

    # create the service for google drive and google sheet
    googleService = gService()

    #create the folder
    kovaakFolder = gFolder(googleService.get('drive'), folderName)


    # create spreadsheets for each playlist
    for title, playlist in playLists.items() :
        # get the kovaak's data for the specific playlist from the steam library
        kovaakData = Ch.Challenges(steamLib, playlist)

        # create the spreadsheet for the playlist
        kovaakGoogleSheet = ChallengeSheet(googleService.get('sheet'), googleService.get('drive'), title, kovaakData.getData())

        # create the requests to create the sheets (tabs) for each challenge in the playlist
        for index, (key, value) in enumerate(kovaakGoogleSheet.challenges.items()):
            kovaakGoogleSheet.createSheet(index, key, value)

        # execute requests to generate the sheets
        kovaakGoogleSheet.sendRequests()

        # place created spreadsheet into folder
        kovaakFolder.moveFileHere(kovaakGoogleSheet.ID)

        break # for testing so we only generate one spreadsheet


if __name__=="__main__":
    main()

