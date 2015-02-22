# data-import-adapters

Set of packages to ease the loading of home energy and temperature CSV data.

First in the series is a package to read eGauge historical data from a CSV file or directly from eGauage device using the [eGauge API (PDF)](http://www.egauge.net/docs/egauge-xml-api.pdf)

Next in series...

* eGauge, XML live data
* eMonitor, csv file
* TED, csv file
* HOBO U12 and U23 Temperature/Relative Humidity Data Loggers, csv file

I use these packages to get energy and temperature data into my home performance database. See [home-performance-flask](https://github.com/netplusdesign/home-performance-flask) and [home-performance-ang-flask](https://github.com/netplusdesign/home-performance-ang-flask).

## Installation

Create a virtual environment

`virtualenv env`

Activate the environment

`. env/bin/activate`

Install pytz and nose.

`pip install pytz`

`pip install nose`

## Test

`nosetests`

## Usage

See egauge_demo.py