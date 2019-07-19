from dateutil.parser import *
from datetime import *
from dateutil.relativedelta import *

# Represents two dates, and the range (read: difference) between them

class DateRange:

    def __init__(self, date_list = None):
        self.date_lower = None
        self.date_upper = None
        self.date_range = None
        if not date_list == []:
            if len(date_list) == 2:
                self.date_lower = date_list[0]
                self.date_upper = date_list[1]
                self.date_range = relativedelta(self.date_upper, self.date_lower)

    def get_date_upper(self):
        return self.date_upper

    def get_date_lower(self):
        return self.date_lower

    def get_date_range(self):
        return self.date_range

    def __repr__(self):
        return str(self.date_lower) + ' - ' + str(self.date_upper)

    def __lt__(self, other):
        if self.get_date_lower() == other.get_date_lower():
            return self.get_date_upper() > other.get_date_upper()
        return self.get_date_lower() < other.get_date_lower()
