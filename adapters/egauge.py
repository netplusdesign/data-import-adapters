'''
    Package to read eGauge data directly from device or
    a CSV file downloaded from the device.
    Information on the query paramenters:
    https://www.egauge.net/media/support/docs/egauge-xml-api.pdf
'''
import os
import csv
from datetime import datetime

from urllib.parse import urlencode
from requests.exceptions import HTTPError

import pytz
import requests

class EGauge:
    ''' Construct with base_urls or filename '''
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=expression-not-assigned

    def __init__(self, config):
        # skip header row retuned with eGauge CSV format
        self._skip = 1
        self._url_path = '/cgi-bin/egauge-show'
        # determine number of rows to skip (s). s is in seconds unless
        #  day (d), hour (h) or minute (m) is used.
        #  For hours, use s=3599 which is 1 hour
        self._intervals = {
            'day': 86399,
            'hour': 3599,
            'minute': 59
        }

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

    def time_delta(self, dt_start, dt_end, interval):
        ''' given 2 datetimes, return the duration in interval '''
        # convert datetimes to aware datetimes, so that if range includes daylight savings
        #  then the delta will be correct
        dt_end = self.tzone.localize(dt_end)
        dt_start = self.tzone.localize(dt_start)
        delta = round((dt_end - dt_start).total_seconds() / (interval+1), 1)
        return delta

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

    def get_url_parameters(self):
        ''' Return GET parameters for URL '''
        # ?c              # output in csv format
        # &S              # apparent power V A
        # &s=3599         # skip rows, rows are seconds by default
        # &n=721          # number of rows to return (not counting skips)
        # &f=1417410000   # unix timestamp of the row before the first row to return
        # &C              # delta-compressed data, values are for unit of time only, not cumulative
        # &Z=             # time zone format. See http://pubs.opengroup.org/onlinepubs/009695399/
        #     LST5        # local standard time
        #     LDT4        # local daylight time
        #     %2C M3.2.0  # ,month.week.day ... M = month format, 3 = March, 2 = 2nd week, 0=sunday
        #     %2F 02      # /hour
        #     %3A 00      # :minute
        #     %2C M11.1.0 # ,month.week.day ... M = month format, 11 = Nov, 1 = 1st week, 0=sunday
        #     %2F 02      # /hour
        #     %3A 00      # :minute

        parameters = {}
        # parameters['c'] = None
        # parameters['C'] = None
        parameters['f'] = self.end_date.timestamp()
        parameters['n'] = self.time_delta(self.start_date, self.end_date,\
                                          self._intervals[self.interval]) # duration
        parameters['s'] = self._intervals[self.interval]
        # parameters['S'] = None
        # must add on extra parameters at end. eGauge doesn't like form &c= or &c=c, etc.
        parameters = urlencode(parameters) + '&c&C&S'
        return parameters

    def compose_url(self, base_url):
        ''' Return url with encoded GET parameters. '''
        url = base_url + self._url_path + '?' + self.get_url_parameters()
        return url

    def read_data_from_url(self, url, column):
        ''' Internal method, open single URL and return a generator '''
        try:
            with requests.get(url, stream=True) as device:
                rows = device.iter_lines()
                rows = (row.decode('utf-8') for row in rows)
                for count, row in enumerate(csv.reader(rows)):
                    if count >= self._skip and len(row) > 0:
                        row = self.format_row(row, column)
                        yield row
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')

    def read_data_from_file(self, filename, column):
        ''' Internal method, read data exported from an eGauge file '''
        filename = os.path.join(os.getcwd(), filename)
        with open(filename, 'rU') as resource:
            resource.readline() * self._skip # Skip the header
            reader = csv.reader(resource)
            for row in reader:
                row = self.format_row(row, column)
                yield row

    def read_data(self):
        ''' External method, open URL(s) and return a list of combined values '''
        i, first = 0, True
        result = []
        for location, column in zip(self.locations, self.columns):
            if location.startswith('http'):
                data = self.read_data_from_url(self.compose_url(location), column)
            else:
                data = self.read_data_from_file(location, column)
            for row in data:
                if first:
                    result.append(row)
                else:
                    result[i] = {**result[i], **row}
                i += 1
            i, first = 0, False
        return result
