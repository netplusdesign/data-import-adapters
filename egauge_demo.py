'''
    Module to demo use of eGauge adaptor.
'''
import json
from adapters.egauge import EGauge

def read_data_from_url():
    # egauge1 = http://192.168.1.8
    # egauge2 = http://192.168.1.7

    config = {
        'base_url': 'http://192.168.1.8',
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

    device = EGauge(config)

    i=0
    rows = []
    for row in device.read_data_from_url():
        i = i + 1
        for column in row:
            if row[column] is '':
                print 'Row: %s, column: %s empty, convert value to 0' % (i, column)
                row[column] = 0
        data = {
            "row_id": i,
            "house_id": 0,
            "device_id": 10,
            "date": row['date'],
            "adjusted_load": float(row['used'])*1000 + float(row['gen'])*-1000, 
            "solar": float(row['gen'])*-1000,
            "used": float(row['used'])*1000,
            "water_heater": float(row['water_heater'])*-1000,
            "ashp": float(row['ashp'])*-1000,
            "water_pump": float(row['water_pump'])*-1000,
            "dryer": float(row['dryer'])*-1000,
            "washer": float(row['washer'])*-1000,
            "dishwasher": float(row['dishwasher'])*-1000,
            "stove": float(row['stove'])*-1000
        }
        rows.append(data)
    print json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': '))
    #return rows

    # could change settings and do it again
    # =====================================
    # transition to daylight savings
    start = '2014-03-01 00:00:00'
    end = '2014-04-01 00:00:00'

    # transition to standard time
    #start = '2014-11-01 00:00:00'
    #end = '2014-12-01 00:00:00'

    device.set_date_range(start, end, timezone)

    device.set_columns([
        'date',
        'used',
        'gen',
        'refrigerator',
        'living_room',
        'aux_heat_bedrooms',
        'aux_heat_living',
        'study',
        'barn',
        'basement_west',
        'basement_east',
        'ventilation',
        'ventilation_preheat',
        'kitchen_recept_rt'])

    device.set_interval('hours')

    # for row in device.read_data_from_url():

def read_data_from_file():
    base_path = '/Users/larry/documents/978/data/final/energy-hourly-2014-11eg.csv'

    config = {
        'path': '/Users/larry/documents/978/data/final/energy-hourly-2014-11eg.csv',
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
    device = EGauge(config)

    i=0
    rows = []
    for row in device.read_data_from_file():
        i = i + 1
        for column in row:
            if row[column] is '':
                print 'Row: %s, column: %s empty, convert value to 0' % (i, column)
                row[column] = 0
        data = {
            "row_id": i,
            "house_id": 0,
            "device_id": 10,
            "date": row['date'],
            "adjusted_load": float(row['used'])*1000 + float(row['gen'])*-1000, 
            "solar": float(row['gen'])*-1000,
            "used": float(row['used'])*1000,
            "water_heater": float(row['water_heater'])*-1000,
            "ashp": float(row['ashp'])*-1000,
            "water_pump": float(row['water_pump'])*-1000,
            "dryer": float(row['dryer'])*-1000,
            "washer": float(row['washer'])*-1000,
            "dishwasher": float(row['dishwasher'])*-1000,
            "stove": float(row['stove'])*-1000
        }
        rows.append(data)
    print json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': '))
    #return rows

if __name__ == "__main__":

    read_data_from_url()
    #read_data_from_file()
