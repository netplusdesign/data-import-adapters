'''
    Module to demo use of eGauge adaptor.
'''
import json
from adapters import egauge

def read_data(base_url, start_date_aware, end_date_aware, interval, column_list):
    i=0
    rows = []
    for row in egauge.read_data(base_url, start_date_aware, end_date_aware, interval, column_list):
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

    #egauge = EGauge(base_url1)

    #egauge.set_date_range(start, end, timezone)
    #egauge.set_columns(col_list)
    #egauge.set_interval('hours')
    
    # egauge1
    base_url1 = 'http://192.168.1.8' 
    # egauge2
    #base_url2 = 'http://192.168.1.7'

    # create date in local timezone
    start_dt = egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
    end_dt =   egauge.create_aware_datetime('2014-05-01 00:00:00', 'US/Eastern')
    # transition to daylight savings
    #start_dt = egauge.create_aware_datetime('2014-03-01 00:00:00', 'US/Eastern')
    #end_dt =   egauge.create_aware_datetime('2014-04-01 00:00:00', 'US/Eastern')
    # transition to standard time
    #start_dt = egauge.create_aware_datetime('2014-11-01 00:00:00', 'US/Eastern')
    #end_dt =   egauge.create_aware_datetime('2014-12-01 00:00:00', 'US/Eastern')

    interval = 'hour'

    cols_egauge1 = ['date','used','gen', 'grid', 'solar','solar_plus','water_heater','ashp','water_pump','dryer','washer','dishwasher','stove']
    #cols_egauge2 = ['date','used','gen', 'refrigerator', 'living_room','aux_heat_bedrooms','aux_heat_living','study','barn','basement_west','basement_east','ventilation','ventilation_preheat','kitchen_recept_rt']

    read_data(base_url1, start_dt, end_dt, interval, cols_egauge1)
