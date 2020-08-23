import kovaak.challenges as Ch
from challengeSheet import ChallengeSheet
from sys import platform
import logging
from myG.gservice import gService
from myG.gdrive import gFolder, findFile
import kovaak.playlist

logging.basicConfig(level=logging.WARNING)
logging.propagate = False
# user inputs:
# steam library path
# Kovaak playlist
# Spreadsheet title

def main ():
    folderName = 'FPS Aim Trainer Stats'
    #use an arg for the steam library path
    # steamLibPath = 'C:/Program Files (x86)/Steam'
    #change path based on OS; maybe put this into args later
    logging.warning('current OS: ', platform)
    if platform == "linux" or platform =="linux2":
        steamLibStats = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
        steamLibPlaylist = '/mnt/c/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/Saved/SaveGames/Playlists'
    elif platform == "win32":
        steamLibStats = 'C:/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/stats'
        steamLibPlaylist = 'C:/Program Files (x86)/Steam/steamapps/common/FPSAimTrainer/FPSAimTrainer/Saved/SaveGames/Playlists'


    # get the playlists from the kovaak's game folder
    playlists = kovaak.playlist.getPlaylists(steamLibPlaylist)
    for i,pl in enumerate(playlists) :
        print(f"{i}. {pl}\t{playlists[pl]}")
    # get the useres input on which playlists to use 
    print('\nType the number of the playlist that you want to use to generate a google sheet.\nMultiple palylists can be selected, please seperate using a comma.\nExample: 0,1,13')
    selection = input()
    selection = selection.split(',')

    inputPlaylists = {}
    for n in selection :
        n = int(n)
        indexedPlaylist = list(playlists.items())[n]
        inputPlaylists[indexedPlaylist[0]] = indexedPlaylist[1]

    print('Selected Playlist(s): ')
    for pl in inputPlaylists :
        print(f"{pl}: {inputPlaylists[pl]}")


    print('Would you like to start creating the google spreadsheet(s)? y/n')
    makeSheets = input()
    if not (makeSheets == 'y' or makeSheets == 'Y') :
        print('Existing App')
        return



    # create the service for google drive and google sheet
    googleService = gService()

    #create the folder
    kovaakFolder = gFolder(googleService.get('drive'), folderName)


    # create spreadsheets for each playlist
    for title, playlist in inputPlaylists.items() :
        # get the kovaak's data for the specific playlist from the steam library
        kovaakData = Ch.Challenges(steamLibStats, title, playlist)

        # create the spreadsheet for the playlist
        kovaakGoogleSheet = ChallengeSheet(googleService.get('sheet'), googleService.get('drive'), title, kovaakData.getData())

        # create the requests to create the sheets (tabs) for each challenge in the playlist
        for index, (key, value) in enumerate(kovaakGoogleSheet.challenges.items()):
            kovaakGoogleSheet.createSheet(index, key, value)

        # execute requests to generate the sheets
        kovaakGoogleSheet.sendRequests()

        # place created spreadsheet into folder
        kovaakFolder.moveFileHere(kovaakGoogleSheet.ID)

if __name__=="__main__":
    main()

