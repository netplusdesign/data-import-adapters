'''
    Module to demo use of eGauge adaptor.
'''
from datetime import datetime
import json
from adapters.egauge import EGauge

egauge1 = 'http://192.168.2.27'
egauge2 = 'http://192.168.2.28'
filename1 = 'tests/test-data/energy-hourly-2015-11eg.csv'
filename2 = 'tests/test-data/energy-hourly-2015-11eg2.csv'
'''
    Note: sequence of columns must align with output from eGauge register.
'''
eg1_col_list = [
                'date',
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
                'stove'
               ]

eg2_col_list = [
                'date_dup',
                'used_dup',
                'gen_dup',
                'refrigerator',
                'living_room',
                'aux_heat_bedrooms',
                'aux_heat_living',
                'study',
                'barn',
                'basement_west',
                'basement_east',
                'kitchen_recept_rt',
                'ventilation'
               ]
# older file format
eg2x_col_list = [
                'date_dup',
                'used_dup',
                'gen_dup',
                'refrigerator',
                'living_room',
                'aux_heat_bedrooms',
                'aux_heat_living',
                'study',
                'barn',
                'basement_west',
                'basement_east',
                'ventilation',
                'ventilation_pre_heat',
                'kitchen_recept_rt'
               ]
# additional static colunns
ref_columns = {
                'row_id': 0,
                'house_id': 0,
                'device_id': 10
              }

def read_data_from_one_url():

    ''' Single device example, all datetimes are assumed to be local '''

    # Sample date ranges

    # Standard, EST
    #'start_datetime': '2014-04-01 00:00:00',
    #'end_datetime': '2014-05-01 00:00:00',

    # Transition to Daylight Savings Time, EDT
    #'start_datetime': '2014-11-01 00:00:00',
    #'end_datetime': '2014-12-01 00:00:00',

    # Transition to Standard Time, EST
    #'start_datetime': '2020-03-08 00:00:00',
    #'end_datetime': '2020-03-09 00:00:00',

    config = {
        'locations': egauge1,
        'columns': eg1_col_list,
        'start_datetime': '2015-11-01 00:00:00', # inclusive
        'end_datetime': '2015-12-01 00:00:00', # exclusive
        'timezone': 'US/Eastern', # optional, defaults to EST
        'interval': 'hours',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    for row in device.read_data():
        i += 1
        # For each row add calculated value for adjusted load
        adjusted_load = { 'adjusted_load': row['used'] *-1 + row['gen'] }
        # set row_id
        ref_columns['row_id'] = i
        # And make date a string
        row['date'] = str(row['date'])
        # join them all together and add to list
        rows.append({**row, **adjusted_load, **ref_columns})
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

    # could change settings and do it again

    # transition to daylight savings
    start = '2014-03-01 00:00:00'
    end = '2014-04-01 00:00:00'

    # transition to standard time
    #start = '2014-11-01 00:00:00'
    #end = '2014-12-01 00:00:00'

    device.set_date_range(start, end)

    # for row in device.read_data_from_urls():

def read_data_from_two_urls():

    ''' Multiple device example, aggrigates data across devices for the same timeframe '''

    config = {
        'locations': [egauge1, egauge2],
        'columns': [eg1_col_list, eg2_col_list],
        'start_datetime': '2015-11-01 00:00:00',
        'end_datetime': '2015-12-01 00:00:00',
        'interval': 'hours',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    for row in device.read_data():
        i += 1
        if row['date'] == row['date_dup']:
            # For each row add calculated value for adjusted load
            adjusted_load = { 'adjusted_load': row['used'] *-1 + row['gen'] }
            # set row_id
            ref_columns['row_id'] = i
            # And make date a string
            row['date'] = str(row['date'])
            row['date_dup'] = str(row['date_dup'])
            #row['date_dup'] = str(row['date_dup'])
            # join them all together and add to list
            rows.append({**row, **adjusted_load, **ref_columns})
        else:
            print(f"dates don't match, row: {i}")
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

def read_data_from_file():

    ''' Read data from a file exported from eGauge '''

    config = {
        'locations': filename1,
        'columns': eg1_col_list,
        'start_datetime': '2015-11-01 00:00:00',
        'end_datetime': '2015-12-01 00:00:00',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    for row in device.read_data():
        i += 1
        # For each row add calculated value for adjusted load
        adjusted_load = { 'adjusted_load': row['used'] *-1 + row['gen'] }
        # set row_id
        ref_columns['row_id'] = i
        # And make date a string
        row['date'] = str(row['date'])
        # join them all together and add to list
        rows.append({**row, **adjusted_load, **ref_columns})
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

def read_data_from_files():

    ''' Read data from 2 files exported from eGauge and join together '''

    config = {
        'locations': [ filename1, filename2 ],
        'columns': [ eg1_col_list, eg2_col_list ],
        'start_datetime': '2015-11-01 00:00:00',
        'end_datetime': '2015-12-01 00:00:00',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    for row in device.read_data():
        i += 1
        if row['date'] == row['date_dup']:
            # For each row add calculated value for adjusted load
            adjusted_load = { 'adjusted_load': row['used'] *-1 + row['gen'] }
            # set row_id
            ref_columns['row_id'] = i
            # And make date a string
            row['date'] = str(row['date'])
            row['date_dup'] = str(row['date_dup'])
            # join them all together and add to list
            rows.append({**row, **adjusted_load, **ref_columns})
        else:
            print(f"dates don't match, row: {i}")
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

if __name__ == "__main__":

    read_data_from_file()
    #read_data_from_files()
    #read_data_from_one_url()
    #read_data_from_two_urls()
