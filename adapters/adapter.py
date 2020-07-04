
import os
import csv
from datetime import datetime
import pytz

class Adapter:
    ''' Construct with base_urls or filename '''
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=expression-not-assigned

    def __init__(self, config):

        self._skip = 0
        self._url_path = ''
        self._intervals = {}

        try:
            self.set_locations(config['locations'])
        except KeyError:
            pass

        try:
            self.set_date_range(config['start_datetime'],
                                config['end_datetime'])
        except KeyError:
            pass

        try:
            self.set_columns(config['columns'])
        except KeyError:
            pass

        try:
            self.set_interval(config['interval'])
        except KeyError:
            pass

        try:
            self.tzone = pytz.timezone(config['timezone'])
        except KeyError:
            # default to eastern timezone
            self.tzone = pytz.timezone('US/Eastern')

        try:
            self.conversion_factor = float(config['conversion_factor'])
        except KeyError:
            self.conversion_factor = 1.0

    def set_locations(self, locations):
        ''' External method to set base url '''
        if isinstance(locations, list):
            self.locations = locations
        elif isinstance(locations, str):
            self.locations = [locations]

    def set_date_range(self, start_date, end_date):
        ''' External method to set duration using date range '''
        self.start_date = self.create_datetime(start_date)
        self.end_date = self.create_datetime(end_date)

    def set_columns(self, columns):
        ''' External method to set columns '''
        if isinstance(columns[0], str):
            self.columns = [columns]
        elif isinstance(columns[0], list):
            self.columns = columns

    def set_interval(self, interval):
        ''' External method, given a keyword, set # of seconds for interval '''
        if 'day' in interval:
            self.interval = 'day'
        elif 'hour' in interval:
            self.interval = 'hour'
        elif 'minute' in interval:
            self.interval = 'hour'

    @staticmethod
    def create_datetime(date_str):
        ''' Internal method to convert string to naive date '''
        date_time = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        return date_time

    def format_row(self, row, columns):
        ''' Internal method to format values in row of data '''
        # row[0] can be a str (from file) or a timestamp (from URL).
        try:
            row[0] = datetime.fromtimestamp(int(row[0]))
        except ValueError:
            row[0] = self.create_datetime(row[0])
        for i in range(1, len(row)):
            row[i] = float(row[i]) * self.conversion_factor if row[i] else 0
        row = dict(zip(columns, row))
        return row

    def in_date_range(self, date_time):
        ''' Internal method to check if date is in range for file reads '''
        # if date range exists, then check if in date range
        result = False
        if hasattr(self, 'start_date') and hasattr(self, 'end_date')\
                    and self.start_date <= date_time < self.end_date:
            result = True
        elif hasattr(self, 'start_date') and not(hasattr(self, 'end_date'))\
                    and self.start_date <= date_time:
            result = True
        elif not(hasattr(self, 'start_date')) and hasattr(self, 'end_date')\
                    and date_time < self.end_date:
            result = True
        elif not hasattr(self, 'start_date') and not hasattr(self, 'end_date'):
            result = True
        return result

    def read_data_from_file(self, filename, column):
        ''' Internal method, read data exported from an eGauge file '''
        filename = os.path.join(os.getcwd(), filename)
        with open(filename, encoding="utf8", errors='ignore') as resource:
            for dummy in range(0, self._skip):
                resource.readline() # Skip the header
            reader = csv.reader(resource)
            for row in reader:
                row = self.format_row(row, column)
                yield row

    def read_data(self):
        ''' External method, open URL(s) and return a list of combined values '''
        i, first = 0, True
        result = []
        for location, column in zip(self.locations, self.columns):
            data = self.read_data_from_file(location, column)
            for row in data:
                if first:
                    result.append(row)
                else:
                    result[i] = {**result[i], **row}
                i += 1
            i, first = 0, False
        return result