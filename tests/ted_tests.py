''' TED adapter tests '''

from nose.tools import assert_equal
from urllib.parse import urlparse, parse_qs
from adapters.ted import TED

class TestTEDAdapter():

    @classmethod
    def setup(self):

        config = {
            'locations': 'tests/test-data/energy-hourly-feb-2012-ted.csv',
            'columns': ['date', 'adjusted_load', 'solar', 'used'],
            'start_datetime': '2012-02-01 00:00:00',
            'end_datetime': '2012-03-01 00:00:00'
        }
        self.device = TED(config)

    @classmethod
    def teardown(cls):

        print("Teardown")

    def test_read_data_from_file(self):

        rows = []
        for row in self.device.read_data():
            rows.append({**row})
        total_rows = len(rows)

        assert_equal(total_rows, 696)
        assert_equal(str(rows[0]['date']), '2012-02-29 23:00:00')
        assert_equal(str(rows[695]['date']), '2012-02-01 00:00:00')
        assert_equal(rows[0]['adjusted_load'], 186)
        assert_equal(rows[0]['solar'], -2)
        assert_equal(rows[0]['used'], 188)
