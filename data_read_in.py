import pandas as pd
import datetime

import foosballgame

SHEET_ID = '1hdM3dleaHsLLUpqnYBnNgiaK8rx9i-9TK4qdZafdz-0' # make sure to share sheet and get actual id
SHEET_NAME = '1v1'
FILENAME = 'data/foosball_data.txt'

def read_in_games_from_sheets(sheets=SHEET_ID, sheet_name = SHEET_NAME, copy_to_csv=False,filename=FILENAME):
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
        game_df = game_df[['Winner Name','Loser Name','Winner Score','Loser Score','Winner Color','Date','Number']]
        game_df.to_csv(filename,index=False)
    return games
    
def read_in_games_from_csv(filename=FILENAME):
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

def clean_game_df(game_df):
    game_df = game_df[game_df['Winner Name'].notna()]
    game_df = game_df[['Winner Name','Loser Name','Winner Score','Loser Score','Winner Color','Date','Number']]
    game_df = game_df.astype({'Winner Score':int,'Loser Score':int,'Number':int})
    return game_df