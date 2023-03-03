import pandas as pd
import datetime

import foosballgame
SHEET_ID = '1hdM3dleaHsLLUpqnYBnNgiaK8rx9i-9TK4qdZafdz-0' # make sure to share sheet and get actual id
SHEET_NAME = '1v1'
FILENAME = 'data/foosball_data.xlsx'
"""
Sheet requirements to enforce:
 - 

"""
def read_in_games_from_sheets(sheets=SHEET_ID, sheet_name = SHEET_NAME):
    url = f'https://docs.google.com/spreadsheets/d/{sheets}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    df = pd.read_csv(url)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # remove unnamed columns
    games = []
    for i in range(0,len(df)):
        winner = df.iloc[i]['Winner Name']
        if type(winner) != str:
            break
        loser =  df.iloc[i]['Loser Name']
        winner_score = df.iloc[i]['Winner Score']
        loser_score =  df.iloc[i]['Loser Score']
        winner_color = df.iloc[i]['Winner Color']
        date = df.iloc[i]['Date'] #datetime.strptime(str(df.iloc[i]['Date']),'%d/%m/%Y')
        date = datetime.date(int(date[6:]),int(date[0:2]),int(date[3:5]))
        number = df.iloc[i]['Number']

        game = foosballgame.FoosballGame(winner,loser,winner_score,loser_score,winner_color,date,number)
        games.append(game)
    return games

def read_in_games_from_excel(filename=FILENAME):
    df = pd.read_excel(filename)
    games = []
    for i in range(0,len(df)):
        winner = df.iloc[i]['Winner Name']
        loser =  df.iloc[i]['Loser Name']
        winner_score = df.iloc[i]['Winner Score']
        loser_score =  df.iloc[i]['Winner Score']
        winner_color = df.iloc[i]['Winner Color']
        date = datetime.strptime(df.iloc[i]['Date'],'%d/%m/%Y')
        number = df.iloc[i]['Number']

        game = foosballgame.FoosballGame(winner,loser,winner_score,loser_score,winner_color,date,number)
        games.append(game)
    return games