'''
    Module to demo use of eMonitor adaptor.
'''
from datetime import datetime
import json
from adapters.emonitor import EMonitor

# columns
'''
    Note: sequence of columns must align with output from eMonitor register.
'''
energy_monitor = ['date', 'inactive', 'main1', 'main2', 'solar', 'water_heater', 'ashp1', 'ashp2',
                  'water_pump', 'dryer', 'washer', 'dishwasher', 'stove1', 'stove2', 'ch14', 'ch15',
                  'ch16', 'ch17', 'ch18', 'ch19', 'ch20', 'ch21', 'ch22', 'ch23', 'ch24', 'ch25',
                  'ch26', 'ch27', 'ch28', 'ch29', 'ch30', 'ch31', 'ch32', 'ch33', 'ch34', 'ch35',
                  'ch36', 'ch37', 'ch38', 'ch39', 'ch40', 'ch41', 'ch42', 'ch43', 'ch44', 'ch45',
                  'voltage']

# additional static colunns
ref_columns = {
                'row_id': 0,
                'house_id': 0,
                'device_id': 5
              }

filename1 = 'tests/test-data/energy-hourly-2013-11-emonitor.csv'

def read_data_from_file():

    ''' Read data from a file exported from eMonitor '''

    config = {
        'locations': filename1,
        'columns': energy_monitor,
        'start_datetime': '2013-11-01 00:00:00',
        'end_datetime': '2013-12-01 00:00:00'
    }
    device = EMonitor(config)

    i=0
    rows = []
    for row in device.read_data():
        i += 1
        if device.in_date_range(row['date']):
            # For each row add calculated value for adjusted load
            adjusted_load = { 'adjusted_load': row['main1'] + row['main2'] }
            used = { 'used': (row['main1'] + row['main2']) - row['solar'] }
            ashp = { 'ashp': row['ashp1'] + row['ashp2'] }
            stove = { 'stove': row['stove1'] + row['stove2'] }
            # delete extra channels
            del [row['inactive'], row['main1'], row['main2'], row['ashp1'], row['ashp2'],
                 row['stove1'], row['stove2']]
            # set row_id
            ref_columns['row_id'] = i
            # And make date a string
            row['date'] = str(row['date'])
            # join them all together and add to list
            rows.append({**row, **adjusted_load, **used, **ashp, **stove, **ref_columns})
        else:
            print(f"date not in range, row: {i}")
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

if __name__ == "__main__":

    read_data_from_file()