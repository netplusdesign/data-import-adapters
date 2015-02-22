''' Adapter tests '''

from nose.tools import *
from adapters import egauge

def setup():
    print "Setup"

def teardown():
    print "Teardown"

def test_create_aware_datetime():
    standard_dt = egauge.create_aware_datetime('2014-03-01 00:00:00', 'US/Eastern')
    daylight_dt = egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')

    assert_equal(standard_dt.utcoffset().total_seconds()/3600, -5)
    assert_equal(daylight_dt.utcoffset().total_seconds()/3600, -4)

def test_aware_date_to_timestamp():
    aware_dt = egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
    timestamp = egauge.aware_date_to_timestamp(aware_dt)

    assert_equal(timestamp, 1396310400.0)

def test_time_delta_no_change():
    start_dt = egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
    end_dt = egauge.create_aware_datetime('2014-05-01 00:00:00', 'US/Eastern')
    duration = egauge.time_delta(start_dt, end_dt)

    assert_equal(duration, 720)

def test_time_delta_to_standard():
    start_dt = egauge.create_aware_datetime('2014-11-01 00:00:00', 'US/Eastern')
    end_dt = egauge.create_aware_datetime('2014-12-01 00:00:00', 'US/Eastern')
    duration = egauge.time_delta(start_dt, end_dt)

    assert_equal(duration, 720)

def test_time_delta_to_daylight():
    start_dt = egauge.create_aware_datetime('2014-03-01 00:00:00', 'US/Eastern')
    end_dt = egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
    duration = egauge.time_delta(start_dt, end_dt)

    assert_equal(duration, 744)

def test_set_interval():
    interval = egauge.set_interval('hourslala')

    assert_equal(interval, 3599)

def test_set_url_parameters():
    end_dt = egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
    interval = 3599
    duration = 744
    parameters = egauge.set_url_parameters(end_dt, interval, duration)

    assert_equal(parameters['f'], 1396310400.0)
    assert_equal(parameters['n'], 744)
    assert_equal(parameters['s'], 3599)
    assert_equal(parameters['Z'], 'LST-5.0LDT-4,M3.2.0/02:00,M11.1.0/02:00')

def test_build_url():
    base_url = 'http://www.mydata.com'
    end_dt = egauge.create_aware_datetime('2014-05-01 00:00:00', 'US/Eastern')
    interval = 3599
    duration = 720.0
    parameters = egauge.set_url_parameters(end_dt, interval, duration)
    url = egauge.build_url(base_url, parameters)
    assert_url = 'http://www.mydata.com/cgi-bin/egauge-show?s=3599&n=720.0&Z=LST-5.0LDT-4%2CM3.2.0%2F02%3A00%2CM11.1.0%2F02%3A00&f=1398902400.0&c&C&S'

    assert_equal(url, assert_url)

def test_read_data_from_url():
    # need to learn how to mock access to a url
    pass

