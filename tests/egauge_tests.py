''' eGauge adapter tests '''

from nose.tools import assert_equal
from urllib.parse import urlparse, parse_qs
from adapters.egauge import EGauge

class TestEGaugeAdapter():

    @classmethod
    def setup(self):

        config = {
            'locations': 'http://0.0.0.0',
            'timezone': 'US/Eastern',
            'columns':['date',
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

        print("Teardown")

    def test_time_delta_no_change(self):

        start_dt = self.device.create_datetime('2014-04-01 00:00:00')
        end_dt = self.device.create_datetime('2014-05-01 00:00:00') # 30 days
        duration = self.device.time_delta(start_dt, end_dt, 3599)

        assert_equal(duration, 720)

    def test_time_delta_to_standard(self):

        start_dt = self.device.create_datetime('2014-11-01 00:00:00')
        end_dt = self.device.create_datetime('2014-12-01 00:00:00') # 30 days
        duration = self.device.time_delta(start_dt, end_dt, 3599)

        assert_equal(duration, 721.0) # time change adds an hour

    def test_time_delta_to_daylight(self):

        start_dt = self.device.create_datetime('2014-03-01 00:00:00')
        end_dt = self.device.create_datetime('2014-04-01 00:00:00') # 31 days
        duration = self.device.time_delta(start_dt, end_dt, 3599)

        assert_equal(duration, 743.0) # time change subtracts an hour

    def test_set_interval(self):

        start_dt = self.device.create_datetime('2014-03-01 00:00:00')
        end_dt = self.device.create_datetime('2014-04-01 00:00:00')
        self.device.set_interval('days')
        duration = self.device.time_delta(start_dt, end_dt, self.device._intervals[self.device.interval])

        assert_equal(self.device._intervals[self.device.interval], 86399)
        assert_equal(duration, 31)

    def test_get_url_parameters(self):

        self.device.set_interval('hourslala')
        self.device.set_date_range('2014-03-01 00:00:00', '2014-04-01 00:00:00')
        params = urlparse(self.device.get_url_parameters()).path
        print(f'params: {params}')
        parameters = parse_qs(params)
        print(f'parameters: {parameters}')

        assert_equal(float(parameters['f'][0]), 1396324800.0)
        assert_equal(float(parameters['n'][0]), 743.0)
        assert_equal(float(parameters['s'][0]), 3599)
        #assert_equal(parameters['Z'], 'LST-5.0LDT-4,M3.2.0/02:00,M11.1.0/02:00')

    def test_compose_url(self):

        self.device.set_interval('hourslala')
        self.device.set_date_range('2014-04-01 00:00:00', '2014-05-01 00:00:00')

        url = self.device.compose_url(self.device.locations[0])

        query = urlparse(url).query
        query_components = dict()
        for qc in query.split("&"):
            if '=' in qc:
                items = qc.split("=")
                query_components[items[0]] = items[1]
            else:
                query_components[qc] = ''

        s = query_components["s"]
        assert_equal(s, '3599')

        n = query_components["n"]
        assert_equal(n, '720.0')

        f = query_components["f"]
        assert_equal(f, '1398916800.0')

        #Z = query_components["Z"]
        #assert_equal(Z, 'LST-5.0LDT-4%2CM3.2.0%2F02%3A00%2CM11.1.0%2F02%3A00')

        c = query_components["c"]
        assert_equal(c, '')

        C = query_components["C"]
        assert_equal(C, '')

        S = query_components["S"]
        assert_equal(S, '')

    def test_2_months(self):

        start_dt = self.device.create_datetime('2014-04-01 00:00:00')
        end_dt = self.device.create_datetime('2014-06-01 00:00:00')
        self.device.set_interval('hours')
        duration = self.device.time_delta(start_dt, end_dt, self.device._intervals[self.device.interval])

        assert_equal(duration, 1464.0)

    def test_in_date_range(self):
        # No date range
        dt = self.device.create_datetime('2014-02-01 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, True)

        # Start date only
        self.device.start_date = (self.device.create_datetime('2014-03-01 00:00:00'))
        dt = self.device.create_datetime('2014-03-01 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, True)

        self.device.start_date = (self.device.create_datetime('2014-03-01 00:00:00'))
        dt = self.device.create_datetime('2014-02-01 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, False)

        # End date only
        del self.device.start_date
        self.device.end_date = (self.device.create_datetime('2014-04-01 00:00:00'))
        dt = self.device.create_datetime('2014-03-31 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, True)

        dt = self.device.create_datetime('2014-04-01 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, False)

        # Start and End dates
        self.device.set_date_range('2014-03-01 00:00:00', '2014-04-01 00:00:00')
        dt = self.device.create_datetime('2014-03-01 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, True)

        dt = self.device.create_datetime('2014-03-31 23:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, True)

        dt = self.device.create_datetime('2014-04-01 00:00:00')
        result = self.device.in_date_range(dt)
        assert_equal(result, False)

    def test_read_data_from_file(self):
        self.device.set_locations('tests/test-data/energy-hourly-2015-11eg.csv')
        self.device.set_date_range('2015-11-01 00:00:00', '2015-12-01 00:00:00')
        rows = []
        for row in self.device.read_data():
            rows.append({**row})
        total_rows = len(rows)

        assert_equal(total_rows, 721)
        assert_equal(str(rows[720]['date']), '2015-11-01 00:00:00')
        assert_equal(str(rows[0]['date']), '2015-11-30 23:00:00')
        assert_equal(rows[0]['used'], 0.661196667)
        assert_equal(rows[0]['gen'], -0.005278611)
        assert_equal(rows[0]['grid'], 0.661196667)
        assert_equal(rows[0]['solar'], -0.005278611)
        assert_equal(rows[0]['solar_plus'], -0.000000000)
        assert_equal(rows[0]['water_heater'], 0.000225833)
        assert_equal(rows[0]['ashp'], -0.461380556)
        assert_equal(rows[0]['water_pump'], 0.000076944)
        assert_equal(rows[0]['stove'], -0.008686389)
