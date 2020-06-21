'''
    Module to demo use of eGauge adaptor.
'''
from datetime import datetime
import json
from adapters.egauge import EGauge

egauge1 = 'http://192.168.2.27'
egauge2 = 'http://192.168.2.28'
'''
    Note: sequence of columns must align with output from eGauge register and
    and any additional columns added.
    If combining data from multiple URLs there can be no duplicate
    column names.
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
ref_col_list = [
                'adjusted_load',
                'row_id',
                'house_id',
                'device_id'
               ]


def read_data_from_one_url():

    # single device example
    # all datetimes are assumed to be local
    config = {
        'base_urls': egauge1,
        'start_datetime': '2014-11-01 00:00:00', # inclusive
        'end_datetime': '2014-12-01 00:00:00', # exclusive
        'timezone': 'US/Eastern', # optional, defaults to EST
        'interval': 'hours',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    columns = eg1_col_list + ref_col_list
    for row in device.read_data_from_urls():
        i += 1
        # for each row, add row_id, house_id, device_id...
        ref_columns = [i, 0, 10]
        # and adjusted load
        adjusted_load = [ row[1] *-1 + row[2] ]
        # Also make date a string
        row[0] = str(row[0])
        # Add columns together
        row = row + adjusted_load + ref_columns
        # create a dict using column names
        row = dict(zip(columns, row))
        rows.append(row)
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

    # could change settings and do it again
    # =====================================
    # transition to daylight savings
    start = '2014-03-01 00:00:00'
    end = '2014-04-01 00:00:00'

    # transition to standard time
    #start = '2014-11-01 00:00:00'
    #end = '2014-12-01 00:00:00'

    device.set_date_range(start, end)

    # for row in device.read_data_from_urls():

def read_data_from_two_urls():

    # multiple device example, aggrigates data across devices for the same timeframe
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
        'base_urls': [egauge1, egauge2],
        'start_datetime': '2014-11-01 00:00:00',
        'end_datetime': '2014-12-01 00:00:00',
        'columns': [eg1_col_list, eg2_col_list],
        'interval': 'hours',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    columns = eg1_col_list + eg2_col_list + ref_col_list
    for row in device.read_data_from_urls():
        i += 1
        # for each row, add row_id, house_id, device_id...
        ref_columns = [i, 0, 10]
        # and adjusted load
        adjusted_load = [ row[1] *-1 + row[2] ]
        # Also make dates strings
        row[0] = str(row[0])
        row[13] = str(row[13])
        # Add columns together
        row = row + adjusted_load + ref_columns
        # create a dict using column names
        row = dict(zip(columns, row))
        rows.append(row)
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

def read_data_from_file():

    config = {
        'filename': '/Users/larry/documents/978/data/final/energy-hourly-2014-11eg.csv',
        'start_datetime': '2014-11-01 00:00:00',
        'end_datetime': '2014-12-01 00:00:00',
        'conversion_factor': -1
    }
    device = EGauge(config)

    i=0
    rows = []
    columns = eg1_col_list + ref_col_list
    for row in device.read_data_from_file():
        i += 1
        # for each row, add row_id, house_id, device_id...
        ref_columns = [i, 0, 10]
        # and adjusted load
        adjusted_load = [ row[1] *-1 + row[2] ]
        # Also make date a string
        row[0] = str(row[0])
        # Add columns together
        row = row + adjusted_load + ref_columns
        # create a dict using column names
        row = dict(zip(columns, row))
        rows.append(row)
    print(json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': ')))

if __name__ == "__main__":

    #read_data_from_one_url()
    #read_data_from_two_urls()
    read_data_from_file()
