'''
    Module to demo use of eGauge adaptor.
'''
from datetime import datetime
import pytz
import json
from adapters.egauge import EGauge

egauge1 = 'http://192.168.1.8'
egauge2 = 'http://192.168.1.7'
eg1_col_list = ['date',
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
                'stove']
eg2_col_list = ['date',
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
                'ventilation_preheat',
                'kitchen_recept_rt']

def read_data_from_url():

    # single device example
    config = {
        'base_url': egauge1,
        'start_datetime': '2014-04-01 00:00:00',
        'end_datetime': '2014-05-01 00:00:00',
        'timezone': 'US/Eastern',
        'column_list': eg1_col_list,
        'interval': 'hours'
    }

    device = EGauge(config)

    i=0
    eastern = pytz.timezone('US/Eastern')
    rows = []
    for row in device.read_data_from_url():
        i = i + 1
        for column in row:
            if row[column] is '':
                print 'Row: %s, column: %s empty, convert value to 0' % (i, column)
                row[column] = 0
        # datetimes in device output are UTC
        aware_dt = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
        # convert to local time
        local_dt = eastern.normalize(aware_dt)
        data = {
            "row_id": i,
            "house_id": 0,
            "device_id": 10,
            "date": str(local_dt),
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

    device.set_date_range(start, end, 'US/Eastern')

    device.set_columns(eg2_col_list)

    device.set_interval('hours')

    # for row in device.read_data_from_url():

def read_data_from_urls():

    # multiple device example
    config = {
        'base_url': [egauge1, egauge2],
        'start_datetime': '2014-04-01 00:00:00',
        'end_datetime': '2014-05-01 00:00:00',
        'timezone': 'US/Eastern',
        'column_list': [eg1_col_list, eg2_col_list],
        'interval': 'hours'
    }
    device = EGauge(config)

    i=0
    eastern = pytz.timezone('US/Eastern')
    rows = []
    for row in device.read_data_from_url():
        i = i + 1
        for column in row:
            if row[column] is '':
                print 'Row: %s, column: %s empty, convert value to 0' % (i, column)
                row[column] = 0
        # datetimes in device output are UTC
        aware_dt = datetime.strptime(row['date'], '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.UTC)
        # convert to local time
        local_dt = eastern.normalize(aware_dt)
        data = {
            "row_id": i,
            "house_id": 0,
            "device_id": 10,
            "date": str(local_dt),
            "adjusted_load": float(row['used'])*1000 + float(row['gen'])*-1000, 
            "solar": float(row['gen'])*-1000,
            "used": float(row['used'])*1000,
            "water_heater": float(row['water_heater'])*-1000,
            "ashp": float(row['ashp'])*-1000,
            "water_pump": float(row['water_pump'])*-1000,
            "dryer": float(row['dryer'])*-1000,
            "washer": float(row['washer'])*-1000,
            "dishwasher": float(row['dishwasher'])*-1000,
            "stove": float(row['stove'])*-1000,
            "refrigerator": float(row['refrigerator'])*-1000,
            "living_room": float(row['living_room'])*-1000,
            "aux_heat_bedrooms": float(row['aux_heat_bedrooms'])*-1000,
            "aux_heat_living": float(row['aux_heat_living'])*-1000,
            "study": float(row['study'])*-1000,
            "barn": float(row['barn'])*-1000,
            "basement_west": float(row['basement_west'])*-1000,
            "basement_east": float(row['basement_east'])*-1000,
            "ventilation": float(row['ventilation'])*-1000,
            "ventilation_preheat": float(row['ventilation_preheat'])*-1000,
            "kitchen_recept_rt": float(row['kitchen_recept_rt'])*-1000
        }
        rows.append(data)
    print json.dumps(rows, sort_keys=False, indent=4, separators=(',', ': '))
    #return rows

def read_data_from_file():

    config = {
        'path': '/Users/larry/documents/978/data/final/energy-hourly-2014-11eg.csv',
        'column_list': eg1_col_list,
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
        # datetimes in csv output are already localized and normalized for timezone
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

    #read_data_from_url()
    read_data_from_urls()
    #read_data_from_file()
