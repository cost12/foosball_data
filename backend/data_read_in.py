import datetime
import logging

import pandas as pd

from backend import foosballgame
from backend import event_date
from backend import utils

logger = logging.getLogger(__name__)

SHEET_ID = '1hdM3dleaHsLLUpqnYBnNgiaK8rx9i-9TK4qdZafdz-0'
GAME_SHEET = '1v1'
DATE_SHEET = 'SemesterDates'
GAME_FILENAME = 'data/foosball_data.txt'
DATE_FILENAME = 'data/semester_dates.txt'

GAME_OPTIONS_FILENAME = 'data/games_options.txt'
DATE_OPTIONS_FILENAME = 'data/dates_options.txt'

def read_in_dates_from_sheets(sheets=SHEET_ID, sheet_name = DATE_SHEET, copy_to_csv=False,filename=DATE_FILENAME):
    url = f'https://docs.google.com/spreadsheets/d/{sheets}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    date_df = pd.read_csv(url)
    date_df = clean_date_df(date_df)
    dates = read_df_to_dates(date_df)

    if copy_to_csv:
        date_df.to_csv(filename,index=False)
    return dates

def read_in_dates_from_csv(filename=DATE_FILENAME):
    date_df = pd.read_csv(filename)
    date_df = clean_date_df(date_df)
    return read_df_to_dates(date_df)

def read_in_games_from_sheets(sheets=SHEET_ID, sheet_name = GAME_SHEET, copy_to_csv=False,filename=GAME_FILENAME):
    url = f'https://docs.google.com/spreadsheets/d/{sheets}/gviz/tq?tqx=out:csv&sheet={sheet_name}'
    game_df = pd.read_csv(url)
    logger.debug("%s game size loaded", game_df.shape)
    game_df = clean_game_df(game_df)
    logger.debug("%s cleaned game size", game_df.shape)
    games = read_df_to_games(game_df)
    logger.debug("%s games loaded", len(games))

    if copy_to_csv:
        game_df.to_csv(filename,index=False)
    return games

def read_in_games_from_csv(filename=GAME_FILENAME):
    game_df = pd.read_csv(filename)
    game_df = clean_game_df(game_df)
    return read_df_to_games(game_df)

def read_in_games_options(filename=GAME_OPTIONS_FILENAME) -> list[utils.SheetIdentifier]:
    options_df = pd.read_csv(filename)
    options_lis = []
    for i in range(0, len(options_df)):
        name =  options_df.iloc[i]['Name']
        option_id = options_df.iloc[i]['ID']
        sheet = options_df.iloc[i]['Sheet']
        csv = options_df.iloc[i]['Csv']
        options_lis.append(utils.SheetIdentifier(name, option_id, sheet, csv))
    return options_lis

def read_in_dates_options(filename=DATE_OPTIONS_FILENAME) -> list[utils.SheetIdentifier]:
    return read_in_games_options(filename)

def read_df_to_games(game_df):
    games = []
    for i in range(len(game_df)):
        winner = game_df.iloc[i]['Winner Name']
        if not isinstance(winner, str):
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
    for i in range(len(date_df)):
        name = str(date_df.iloc[i]['Name'])
        if not isinstance(name, str):
            break
        start = date_df.iloc[i]['Start Date']
        end   = date_df.iloc[i]['End Date']
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
    date_df = date_df[date_df['Name'].notna()]
    date_df = date_df[['Name','Start Date','End Date']]
    return date_df
