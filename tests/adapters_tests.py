''' Adapter tests '''

from nose.tools import *
from adapters.egauge import EGauge

class TestEGaugeAdapters():

    @classmethod
    def setup(self):

        config = {
            'base_url': 'http://0.0.0.0',
            'start_datetime': '2014-04-01 00:00:00',
            'end_datetime': '2014-05-01 00:00:00',
            'timezone': 'US/Eastern',
            'column_list':['date',
                           'used',
                           'gen',
                           'grid',
                           'solar',
                           'solar_plus',
                           'water_heater',
                           'ashp',
                           'water_pump',
                           'dryer',
                           'washer',
                           'dishwasher',
                           'stove'],
            'interval': 'hours'
        }
        self.device = EGauge(config)

    @classmethod
    def teardown(cls):

        print "Teardown"

    def test_create_aware_datetime(self):

        assert_equal(self.device.base_url, 'http://0.0.0.0')
        assert_equal(self.device.end_date.utcoffset().total_seconds()/3600, -4)
        assert_equal(self.device.duration, 722)
        assert_equal(self.device.interval, 3599)

    def test_create_aware_datetime(self):

        standard_dt = self.device.create_aware_datetime('2014-03-01 00:00:00', 'US/Eastern')
        daylight_dt = self.device.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')

        assert_equal(standard_dt.utcoffset().total_seconds()/3600, -5)
        assert_equal(daylight_dt.utcoffset().total_seconds()/3600, -4)

    def test_aware_date_to_timestamp(self):

        aware_dt = self.device.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
        timestamp = self.device.aware_date_to_timestamp(aware_dt)
    
        assert_equal(timestamp, 1396324800.0)

    def test_time_delta_no_change(self):

        start_dt = self.device.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
        end_dt = self.device.create_aware_datetime('2014-05-01 00:00:00', 'US/Eastern')
        duration = self.device.time_delta(start_dt, end_dt, 3599)

        assert_equal(duration, 720)

    def test_time_delta_to_standard(self):

        start_dt = self.device.create_aware_datetime('2014-11-01 00:00:00', 'US/Eastern')
        end_dt = self.device.create_aware_datetime('2014-12-01 00:00:00', 'US/Eastern')
        duration = self.device.time_delta(start_dt, end_dt, 3599)

        assert_equal(duration, 721.0)

    def test_time_delta_to_daylight(self):

        start_dt = self.device.create_aware_datetime('2014-03-01 00:00:00', 'US/Eastern')
        end_dt = self.device.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
        duration = self.device.time_delta(start_dt, end_dt, 3599)

        assert_equal(duration, 743.0)

    def test_set_interval(self):

        start_dt = self.device.create_aware_datetime('2014-03-01 00:00:00', 'US/Eastern')
        end_dt = self.device.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
        interval = self.device.set_interval('days')
        duration = self.device.time_delta(start_dt, end_dt, interval)

        assert_equal(self.device.interval, 86399)
        assert_equal(duration, 31)

    def test_get_url_parameters(self):

        self.device.set_interval('hourslala')
        self.device.set_date_range('2014-03-01 00:00:00', '2014-04-01 00:00:00', 'US/Eastern')

        parameters = self.device.get_url_parameters()

        assert_equal(parameters['f'], 1396324800.0)
        assert_equal(parameters['n'], 743.0)
        assert_equal(parameters['s'], 3599)
        assert_equal(parameters['Z'], 'LST-5.0LDT-4,M3.2.0/02:00,M11.1.0/02:00')
    
    def test_get_url(self):

        self.device.set_interval('hourslala')
        self.device.set_date_range('2014-04-01 00:00:00', '2014-05-01 00:00:00', 'US/Eastern')

        url = self.device.get_url()
        assert_url = 'http://0.0.0.0/cgi-bin/egauge-show?s=3599&n=720.0&Z=LST-5.0LDT-4%2CM3.2.0%2F02%3A00%2CM11.1.0%2F02%3A00&f=1398916800.0&c&C&S'

        assert_equal(url, assert_url)

    def test_2_months(self):

        start_dt = self.device.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
        end_dt = self.device.create_aware_datetime('2014-06-01 00:00:00', 'US/Eastern')
        interval = self.device.set_interval('hours')
        duration = self.device.time_delta(start_dt, end_dt, interval)

        assert_equal(duration, 1464.0)

    def xtest_read_data_from_url(self):
        # need to learn how to mock access to a url
        pass
