''' eMonitor adapter tests '''

from nose.tools import assert_equal
from urllib.parse import urlparse, parse_qs
from adapters.emonitor import EMonitor

class TestEMonitorAdapter():

    @classmethod
    def setup(self):

        config = {
            'locations': 'tests/test-data/energy-hourly-2013-11-emonitor.csv',
            'columns':['date', 'inactive', 'main1', 'main2', 'solar', 'water_heater', 'ashp1',
                       'ashp2', 'water_pump', 'dryer', 'washer', 'dishwasher', 'stove1', 'stove2',
                       'ch14', 'ch15', 'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22',
                       'ch23', 'ch24', 'ch25', 'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31',
                       'ch32', 'ch33', 'ch34', 'ch35', 'ch36', 'ch37', 'ch38', 'ch39', 'ch40',
                       'ch41', 'ch42', 'ch43', 'ch44', 'ch45', 'voltage'],
            'start_datetime': '2013-11-01 00:00:00',
            'end_datetime': '2013-12-01 00:00:00'
        }
        self.device = EMonitor(config)

    @classmethod
    def teardown(cls):

        print("Teardown")

    def test_read_data_from_file(self):

        rows = []
        for row in self.device.read_data():
            rows.append({**row})
        total_rows = len(rows)

        assert_equal(total_rows, 720)
        assert_equal(str(rows[0]['date']), '2013-11-01 00:00:00')
        assert_equal(str(rows[719]['date']), '2013-11-30 23:00:00')
        assert_equal(rows[0]['main1'], 195)
        assert_equal(rows[0]['main2'], 266)
        assert_equal(rows[0]['solar'], 0)
        assert_equal(rows[0]['water_heater'], 0)
        assert_equal(rows[0]['ashp1'], 128)
        assert_equal(rows[0]['ashp2'], 129)
        assert_equal(rows[0]['water_pump'], 0)
        assert_equal(rows[0]['stove1'], 6)
        assert_equal(rows[0]['stove2'], 2)
        assert_equal(rows[0]['voltage'], 125.2)
