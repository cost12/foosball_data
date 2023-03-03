

import userinput
import data_read_in

def mainSheets():
    games = data_read_in.read_in_games_from_sheets()
    userinput.interaction(games)

def mainExcel():
    games = data_read_in.read_in_games_from_excel()
    userinput.interaction(games)


if __name__=="__main__":
    if 1:
        mainSheets()
    else:
        mainExcel()