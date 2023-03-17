import pandas as pd
import datetime

import foosballgame
import event_date

SHEET_ID = '1hdM3dleaHsLLUpqnYBnNgiaK8rx9i-9TK4qdZafdz-0' # make sure to share sheet and get actual id
GAME_SHEET = '1v1'
DATE_SHEET = 'SemesterDates'
GAME_FILENAME = 'data/foosball_data.txt'
DATE_FILENAME = 'data/semester_dates.txt'

def read_in_dates_from_sheets(sheets=SHEET_ID, sheet_name = DATE_SHEET, copy_to_csv=False,filename=DATE_FILENAME):
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sheets}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        date_df = pd.read_csv(url)
        date_df = clean_date_df(date_df)
        dates = read_df_to_dates(date_df)
    except Exception as e:
        print("Error reading in from sheets, attempting to read from csv")
        print(e)
        dates = read_in_dates_from_csv()
    if copy_to_csv:
        date_df.to_csv(filename,index=False)
    return dates

def read_in_dates_from_csv(filename=DATE_FILENAME):
    try:
        date_df = pd.read_csv(filename)
        date_df = clean_date_df(date_df)
        return read_df_to_dates(date_df)
    except Exception as e:
        print("Error: data read from csv failed")
        print(e)
        return None

def read_in_games_from_sheets(sheets=SHEET_ID, sheet_name = GAME_SHEET, copy_to_csv=False,filename=GAME_FILENAME):
    try:
        url = f'https://docs.google.com/spreadsheets/d/{sheets}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
        game_df = pd.read_csv(url)
        game_df = clean_game_df(game_df)
        games = read_df_to_games(game_df)
    except Exception as e:
        print("Error reading in from sheets, attempting to read from csv")
        print(e)
        games = read_in_games_from_csv()
    if copy_to_csv:
        game_df.to_csv(filename,index=False)
    return games
    
def read_in_games_from_csv(filename=GAME_FILENAME):
    try:
        game_df = pd.read_csv(filename)
        game_df = clean_game_df(game_df)
        return read_df_to_games(game_df)
    except Exception as e:
        print("Error: data read from csv failed")
        print(e)
        return None


def read_df_to_games(game_df):
    games = []
    for i in range(0,len(game_df)):
        winner = game_df.iloc[i]['Winner Name']
        if type(winner) != str:
            break
        loser =  game_df.iloc[i]['Loser Name']
        winner_score = game_df.iloc[i]['Winner Score']
        loser_score =  game_df.iloc[i]['Loser Score']
        winner_color = game_df.iloc[i]['Winner Color']
        date = game_df.iloc[i]['Date'] #datetime.strptime(str(game_df.iloc[i]['Date']),'%d/%m/%Y')
        date = datetime.date(int(date[6:]),int(date[0:2]),int(date[3:5]))
        number = game_df.iloc[i]['Number']

        game = foosballgame.FoosballGame(winner,loser,winner_score,loser_score,winner_color,date,number)
        games.append(game)
    return games

def read_df_to_dates(date_df):
    dates = []
    for i in range(0,len(date_df)):
        name = 'Semester ' + str(date_df.iloc[i]['Semester Number'])
        if type(name) != str:
            break
        start = date_df.iloc[i]['Semester Start Date']
        end   = date_df.iloc[i]['Semester End Date']
        start_date = datetime.date(int(start[6:]),int(start[0:2]),int(start[3:5]))
        end_date = datetime.date(int(end[6:]),int(end[0:2]),int(end[3:5]))

        date = event_date.EventDate(name,start_date,end_date)
        dates.append(date)
    return dates

def clean_game_df(game_df):
    game_df = game_df[game_df['Winner Name'].notna()]
    game_df = game_df[['Winner Name','Loser Name','Winner Score','Loser Score','Winner Color','Date','Number']]
    game_df = game_df.astype({'Winner Score':int,'Loser Score':int,'Number':int})
    return game_df

def clean_date_df(date_df):
    date_df = date_df[date_df['Semester Number'].notna()]
    date_df = date_df[['Semester Number','Semester Start Date','Semester End Date']]
    date_df = date_df.astype({'Semester Number':int})
    return date_df