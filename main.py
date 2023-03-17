import sys

import userinput
import data_read_in
import data_visualizer

def mainPrint(save_csv=False,use_csv=False):
    if use_csv:
        games = data_read_in.read_in_games_from_csv()
    else:
        games = data_read_in.read_in_games_from_sheets(copy_to_csv=save_csv)
    if games is not None:
        userinput.interaction(games)

def mainVisualize(save_csv=False,use_csv=False):
    if use_csv:
        games = data_read_in.read_in_games_from_csv()
        dates = data_read_in.read_in_dates_from_csv()
    else:
        games = data_read_in.read_in_games_from_sheets(copy_to_csv=save_csv)
        dates = data_read_in.read_in_dates_from_sheets(copy_to_csv=save_csv)
    if games is not None:
        data_visualizer.visualize_foosball(games,dates)

def main():
    to_run = 'vis'
    save_csv = False
    use_csv = False

    if 'save' in sys.argv:
        save_csv = True
    if 'csv' in sys.argv:
        use_csv = True
    if len(sys.argv) >= 2:
        to_run = sys.argv[1]
    elif len(sys.argv) > 2:
        print("Error: expecing 0 or 1 arguments")

    if to_run in ['vis', 'v']:
        mainVisualize(save_csv, use_csv)
    elif to_run in ['print','p']:
        mainPrint(save_csv, use_csv)
    else:
        print("Error: invalid command {} expecting vis or print".format(to_run))

if __name__=="__main__":
    main()