class SheetIdentifier:

    def __init__(self, name, id, sheet, csv = None) -> None:
        self.name = name          # readable name
        self.id = id              # id of shared sheet
        self.sheet_name = sheet   # name of sheet within the google sheets doc
        self.csv_name = csv       # name of the csv associated with the google sheets

        # name should be unique for all
        # csv_name should be unique for all