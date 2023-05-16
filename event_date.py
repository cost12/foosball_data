class EventDate:

    def __init__(self,n,s,e):
        self.name = n
        self.start_date = s
        self.end_date = e

    """
    Checks wether a given date falls within the range [inclusive, exclusive)
    """
    def contains_date(self, date):
        return self.start_date <= date and date < self.end_date