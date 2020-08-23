# Aim Trainer Stat Cruncher
Play Kovaak's Aim Trainer? Want your data in google sheets? say no more...

## Usage
Requirements:
  * python (preferably python 3.8 and above).
  * Requires familiarity creating a google cloud project.
  * Requires game data from Kovaak's FPS Aim Trainer (steam/windows)

1. Create a google cloud project and enable the drive and sheets API.
2. Generate the credentials.json for the google cloud project and put it into the root folder of this project.
3. Run the app using `python3 app.py` or `python app.py`.
4. Select the playlists that you want to create google sheets for. Each sheet will include graphs of accuracy and score performance.

WARNING: If .csv files are deleted from `./data/` some functionality will break. It is advised to delete all related sheets and folders from your google drive if this occurs as well as all local .csv files in `./data/`.

## How it works
1. Playlist data is loaded from the steam library.
2. Stats data is loaded from the steam library for the selected playlist(s).
  1. Checked files are stored in the *-checkedData.csv files.
  2. When running, files that have already been checked will be skipped.
  3. *-checkedData.csv is updated.
3. A google folder is created. The name and ID of the folder is saved to gdrivedata.csv.
4. A google spreadsheet is created for each playlist.
  1. If the spreadsheet already exists, new Stats data will be appended.
  2. If the spreadsheet does not exist, a new spreadsheet will be created. The name and ID of the spreadsheet is saved to gdrivedata.csv. Data, tables, and sheets will be created for the new spreadsheet using Stats data.
5. Spreadsheets are moved to the google folder.
