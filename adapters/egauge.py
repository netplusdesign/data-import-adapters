'''
    Package to read eGauge data directly from device.
'''
import csv

from urllib2 import urlopen, URLError
from urllib import urlencode

from datetime import datetime
import pytz

class EGauge(object):
    ''' Construct with base_url or filepath '''

    def __init__(self, config):
        try:
            if type(config['base_url']) is str:
                self.base_url = [ config['base_url'] ]
            else:
                self.base_url = config['base_url']
        except KeyError:
            pass

        try:
            self.path = config['path']
        except KeyError:
            pass

        try:
            self.set_date_range(config['start_datetime'],
                                config['end_datetime'],
                                config['timezone'])
            self.interval = self.set_interval(config['interval'])
        except KeyError:
            pass

        try:
            if type(config['column_list'][0]) is str:
                self.columns = [ config['column_list'] ]
            else:
                self.columns = config['column_list']
        except KeyError:
            pass

        # skip header row retuned with CSV format
        self.skip = 1

    def set_base_url(self, base_url):
        ''' External method to set base url '''
        self.base_url = base_url

    def set_path(self, path):
        ''' External method to set filepath '''
        self.path = path

    def set_date_range(self, start_date, end_date, timezone):
        ''' External method to set duration and timestamp using date range '''
        self.start_date = self.create_aware_datetime(start_date, timezone)
        self.end_date = self.create_aware_datetime(end_date, timezone)
        #self.end_timestamp = self.aware_date_to_timestamp(self.end_date)
        #self.duration = self.time_delta(start_date, self.end_date)

    def set_interval(self, interval):
        ''' External methid, given a keyword, set # of seconds for interval '''
        # determine number of rows to skip (s). s is in seconds unless
        #  day (d), hour (h) or minute (m) is used.
        #  For hours, use s=3599 which is 1 hour
        if 'day' in interval:
            self.interval = 86399
        elif 'hour' in interval:
            self.interval = 3599
        elif 'minute' in interval:
            self.interval = 59
        return self.interval

    def set_columns(self, columns):
        ''' External method to set column list '''
        self.columns = columns

    @classmethod
    def create_aware_datetime(cls, date_string, zone):
        ''' Return a timezone aware datetime '''
        fmt = '%Y-%m-%d %H:%M:%S'
        tzone = pytz.timezone(zone)
        date = tzone.localize(datetime.strptime(date_string, fmt))
        return date

    @classmethod
    def aware_date_to_timestamp(cls, aware_dt):
        ''' Given a timezone aware datetime, return a unix timestamp duration in hours '''
        epoch = datetime(1970, 01, 01, 0, 0, 0, 0, tzinfo=pytz.utc)
        # convert aware_dt to utc
        utc_aware_dt = aware_dt.astimezone(pytz.utc)
        # subtract for timedelta
        timestamp = (utc_aware_dt - epoch).total_seconds()
        return timestamp

    @classmethod
    def time_delta(cls, dt_start, dt_end, interval):
        ''' given 2 datetimes, return the duration in hours '''
        delta = (dt_end - dt_start).total_seconds() / (interval+1)
        return round(delta)

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
        tz_parameters = {}
        tz_parameters['LST'] = self.end_date.tzinfo.utcoffset(datetime(self.end_date.year, 1, 1, 0, 0, 0)).\
                                total_seconds()/3600 # 5hrs for EST
        tz_parameters['LST_M'] = 3                  # US only, need to fix
        tz_parameters['LST_W'] = 2                  # ditto
        tz_parameters['LST_D'] = 0                  # ditto
        tz_parameters['LST_h'] = '{:02}'.format(2)  # 2 am
        tz_parameters['LST_m'] = '{:02}'.format(0)
        tz_parameters['LDT'] = self.end_date.tzinfo.utcoffset(datetime(self.end_date.year, 6, 1, 0, 0, 0)).\
                                total_seconds()/3600 # 4hrs for EDT
        tz_parameters['LDT_M'] = 11                 # US only, need to fix
        tz_parameters['LDT_W'] = 1                  # ditto
        tz_parameters['LDT_D'] = 0                  # ditto
        tz_parameters['LDT_h'] = '{:02}'.format(2)  # 2 am
        tz_parameters['LDT_m'] = '{:02}'.format(0)

        parameters = {}
        #parameters['c'] = 'c'
        #parameters['C'] = 'C'
        parameters['f'] = self.aware_date_to_timestamp(self.end_date)
        parameters['n'] = self.time_delta(self.start_date, self.end_date, self.interval) # duration
        parameters['s'] = self.interval
        #parameters['S'] = 'S'
        parameters['Z'] = 'LST%(LST)sLDT%(LDT)u,M%(LST_M)u.%(LST_W)u.%(LST_D)u/%(LST_h)s:%(LST_m)s,M%(LDT_M)u.%(LDT_W)u.%(LDT_D)u/%(LDT_h)s:%(LDT_m)s' % tz_parameters
        return parameters

    def compose_url(self, base_url):
        ''' Return url with encoded GET parameters. '''
        path = '/cgi-bin/egauge-show'
        # must add on extra parameters at end. eGauge doesn't like form &c= or &c=c, etc.
        url = base_url + path + '?' + urlencode(self.get_url_parameters()) + '&c&C&S'
        # print '# %s' % url
        return url

    def read_data_from_urls(self, url, cols):
        ''' Internal method, open single URL and return a generator '''
        try:
            resource = urlopen(url)
            resource.readline() * self.skip # Skip the header
            reader = csv.DictReader(resource, fieldnames=cols)
            for row in reader:
                yield row
            resource.close()
        except URLError as e:
            if hasattr(e, 'reason'):
                print 'Failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code

    def read_data_from_url(self):
        ''' External method, open URL(s) and return a list of combined values '''
        i, first = 0, True
        result = []
        for uri, column in zip(self.base_url, self.columns):
            for row in self.read_data_from_urls(self.compose_url(uri), column):
                if first:
                    result.append(row)
                else:
                    result[i].update(row)
                i = i + 1
            i, first = 0, False
        return result

    def read_data_from_file(self):
        ''' As function says... '''
        with open(self.path, 'rU') as resource:
            #return self.parse_file(resource, self.columns, self.EGAUGE_SKIP)
            resource.readline() * self.skip # Skip the header
            reader = csv.DictReader(resource, fieldnames=self.columns)
            for row in reader:
                yield row
