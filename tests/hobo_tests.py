''' Hobo adapter tests '''

from nose.tools import assert_equal
from urllib.parse import urlparse, parse_qs
from adapters.hobo import Hobo

class TestHoboAdapter():

    @classmethod
    def setup(self):

        config = {
            'locations': 'tests/test-data/temperature-hourly-outdoor-2012-02-01-to-2012-11-30.csv',
            'columns': ['date', 'temperature', 'humidity'],
            'start_datetime': '2012-03-01 00:00:00',
            'end_datetime': '2012-04-01 00:00:00'
        }
        self.device = Hobo(config)

    @classmethod
    def teardown(cls):

        print("Teardown")

    def test_read_data_from_file(self):

        rows = []
        for row in self.device.read_data():
            rows.append({**row})
        total_rows = len(rows)

        assert_equal(total_rows, 744)
        assert_equal(str(rows[0]['date']), '2012-03-01 00:00:00')
        assert_equal(str(rows[743]['date']), '2012-03-31 23:00:00')
        assert_equal(rows[0]['temperature'], 31.239)
        assert_equal(rows[0]['humidity'], 93.147)
