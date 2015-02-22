'''
    Package to read eGauge data directly from device.
'''
import csv

from urllib2 import urlopen, URLError
from urllib import urlencode

from datetime import datetime
import pytz

# skip header row retuned with CSV format
EGAUGE_SKIP = 1

def read_data_from_file(path, cols):
    ''' As function says... '''
    with open(path, 'rU') as data:
        return parse_file(data, cols)

def create_aware_datetime(date_string, zone):
    ''' Return a timezone aware datetime '''
    fmt = '%Y-%m-%d %H:%M:%S'
    tzone = pytz.timezone(zone)
    date = tzone.localize(datetime.strptime(date_string, fmt))
    return date

def aware_date_to_timestamp(aware_dt):
    ''' Given a timezone aware datetime, return a unix timestamp duration in hours '''
    epoch = datetime(1970, 01, 01, 0, 0, 0, 0, tzinfo=pytz.utc)
    # get offset on seconds
    offset = aware_dt.utcoffset().total_seconds()
    # convert aware_dt to utc
    utc_aware_dt = aware_dt.astimezone(pytz.utc)
    # subtract for timedelta
    timestamp = (utc_aware_dt - epoch).total_seconds()
    timestamp = timestamp + offset
    return timestamp

def time_delta(dt_start, dt_end):
    ''' given 2 datetimes, return the duration in hours '''
    # switch to daylight time, subtract 1 from n (2 pm is missing)
    # tz_start = eastern.utcoffset(datetime(2014,3,1,0,0,0)).\
    #            total_seconds()/3600 # = -14400/3600 = -5 hrs
    # tz_end   = eastern.utcoffset(datetime(2014,4,1,0,0,0)).\
    #            total_seconds()/3600 # = -18000/3600 = -4 hrs
    # (-4) - (-5) = 1
    # switch to standard time, add 1 to n value (there are 2 1am rows)
    # tz_start = eastern.utcoffset(datetime(2014,11,1,0,0,0)).\
    #            total_seconds()/3600 # = -14400/3600 = -4 hrs
    # tz_end   = eastern.utcoffset(datetime(2014,12,1,0,0,0)).\
    #            total_seconds()/3600 # = -18000/3600 = -5 hrs
    # (-5) - (-4) = -1
    try:
        start_offset = dt_start.utcoffset().total_seconds() / 3600
        end_offset = dt_end.utcoffset().total_seconds() / 3600
        offset = end_offset - start_offset
    except AttributeError:
        offset = 0
    delta_hours = (dt_end - dt_start).total_seconds() / 3600
    return delta_hours + offset

def set_interval(interval):
    ''' Given a keyword, return # of seconds for interval '''
    # determine number of rows to skip (s). s is in seconds unless
    #  day (d), hour (h) or minute (m) is used.
    #  For hours, use s=3599 which is 1 hour
    if 'day' in interval:
        return 86399
    elif 'hour' in interval:
        return 3599
    elif 'minute' in interval:
        return 59

def set_url_parameters(end_dt, interval, duration):
    ''' Return GET parameters for URL '''
    # ?c              # output in csv format
    # &S              # apparent power V A
    # &s=3599         # skip rows, rows are seconds by default
    # &n=721          # number of rows to return (not counting skips)
    # &f=1417410000   # unix timestamp of the row before the first row to return
    # &C              # delta-compressed data, values are for that unit of time only, not cumulative
    # &Z=             # time zone format as per (http://pubs.opengroup.org/onlinepubs/009695399/)
    #     LST5        # local standard time
    #     LDT4        # local daylight time
    #     %2C M3.2.0  # ,month.week.day ... M = month format, 3 = March, 2 = 2nd week, 0=sunday
    #     %2F 02      # /hour
    #     %3A 00      # :minute
    #     %2C M11.1.0 # ,month.week.day ... M = month format, 11 = Nov, 1 = 1st week, 0=sunday
    #     %2F 02      # /hour
    #     %3A 00      # :minute
    tz_parameters = {}
    tz_parameters['LST'] = end_dt.tzinfo.utcoffset(datetime(end_dt.year, 1, 1, 0, 0, 0)).\
                            total_seconds()/3600 # 5hrs for EST
    tz_parameters['LST_M'] = 3                  # US only, need to fix
    tz_parameters['LST_W'] = 2                  # ditto
    tz_parameters['LST_D'] = 0                  # ditto
    tz_parameters['LST_h'] = '{:02}'.format(2)  # 2 am
    tz_parameters['LST_m'] = '{:02}'.format(0)
    tz_parameters['LDT'] = end_dt.tzinfo.utcoffset(datetime(end_dt.year, 6, 1, 0, 0, 0)).\
                            total_seconds()/3600 # 4hrs for EDT
    tz_parameters['LDT_M'] = 11                 # US only, need to fix
    tz_parameters['LDT_W'] = 1                  # ditto
    tz_parameters['LDT_D'] = 0                  # ditto
    tz_parameters['LDT_h'] = '{:02}'.format(2)  # 2 am
    tz_parameters['LDT_m'] = '{:02}'.format(0)

    parameters = {}
    #parameters['c'] = 'c'
    #parameters['C'] = 'C'
    parameters['f'] = aware_date_to_timestamp(end_dt)   # 1417410000 = timestamp 2014-12-01 00:00:00
    parameters['n'] = duration                  # 721 = 30 days in Nov over timechange
    # map end or start+duration to first (f) row to be returned. This row is not returned.
    #  Example: to start on Nov 30 23:00:00, f must be Dec 1 at 00:00:00.
    parameters['s'] = interval                  # 3599 = hour
    #parameters['S'] = 'S'
    parameters['Z'] = 'LST%(LST)sLDT%(LDT)u,M%(LST_M)u.%(LST_W)u.%(LST_D)u/%(LST_h)s:%(LST_m)s,M%(LDT_M)u.%(LDT_W)u.%(LDT_D)u/%(LDT_h)s:%(LDT_m)s' % tz_parameters
    return parameters

def build_url(base_url, parameters):
    ''' Return url with encoded GET parameters. '''
    path = '/cgi-bin/egauge-show'
    # must add on extra parameters at end. eGauge doesn't like form &c= or &c=c, etc.
    url = base_url + path + '?' + urlencode(parameters) + '&c&C&S'
    # print '# %s' % url
    return url

def read_data_from_url(url, cols):
    ''' Open URL and return a generator '''
    try:
        resource = urlopen(url)
        return parse_file(resource, cols)
    except URLError as e:
        if hasattr(e, 'reason'):
            print 'Failed to reach a server.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code

def parse_file(data, cols):
    ''' Returns a generator '''
    data.readline() * EGAUGE_SKIP # Skip the header
    reader = csv.DictReader(data, fieldnames=cols)
    for row in reader:
        yield row

# read_data(base_url, start_date_aware, duration, interval, column_list)
# read_data(filepath, column_list)
def read_data(base_url, start_date_aware, end_date_aware, interval, column_list):
    ''' Main method, returns CSV data from eGauge device at base_url '''
    # calculate the number (n) of rows to return
    #  (X days * 24 hours +/- daylight savings time changes)
    duration = time_delta(start_date_aware, end_date_aware)
    interval = set_interval(interval)
    parameters = set_url_parameters(end_date_aware, interval, duration)
    url = build_url(base_url, parameters)

    return read_data_from_url(url, column_list)
