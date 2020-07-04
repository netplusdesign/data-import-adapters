'''
    Module to demo use of Hobo temperature adaptor.
'''
from datetime import datetime
import json
from adapters.hobo import Hobo

# columns
'''
    Note: sequence of columns must align with output from Hoboware.
'''
temperature_fields = ['date', 'temperature', 'humidity']

# additional static colunns
ref_columns = {
                'row_id': 0,
                'house_id': 0,
                'device_id': 0
              }

filename1 = 'tests/test-data/temperature-hourly-outdoor-2012-02-01-to-2012-11-30.csv'

def read_data_from_file():

    ''' Read data from a file exported from Hoboware '''

    config = {
        'locations': filename1,
        'columns': temperature_fields,
        'start_datetime': '2012-11-01 00:00:00',
        'end_datetime': '2012-12-01 00:00:00'
    }
    device = Hobo(config)

    i=0
    rows = []
    for row in device.read_data():
        i += 1
        if device.in_date_range(row['date']):
            # set row_id
            ref_columns['row_id'] = i
            # And make date a string
            row['date'] = str(row['date'])
            # join them all together and add to list
            rows.append({**row, **ref_columns})
        else:
            print(f"date not in range, row: {i}")
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

if __name__ == "__main__":

    read_data_from_file()