# data-import-adapters

Set of packages to ease the loading of home energy and temperature CSV data.

* eGauge historical - a package to read eGauge data from a CSV file or directly from eGauage device using the [eGauge API (PDF)](http://www.egauge.net/docs/egauge-xml-api.pdf)
* eMonitor, csv file
* TED, csv file
* HOBO U12 and U23 Temperature/Relative Humidity Data Loggers, csv file

I use these packages to get energy and temperature data into my home performance database. See [home-performance-flask](https://github.com/netplusdesign/home-performance-flask) and [home-performance-ang-flask](https://github.com/netplusdesign/home-performance-ang-flask).

Features:

* Simplifies pulling data from an eGauge device
* When pulling data directly from eGauge device, will check for daylight savings to return the correct duration
* Rudimentry formatting (converts date times to date time objects, and other values to floats)
* Timeframe check, only return data in specified range
* Can join together multiple files or URLs that share the same date time range
* Automatically skips header rows
* Returns each row as a dict

Future:

* eGauge, XML realtime data

## Installation

Create a virtual environment

`python3 -m venv env`

Activate the environment

`source env/bin/activate`

Install dependencies

`pip install -r requirements.txt`

## Test

`nosetests`

## Usage

See egauge_demo.py

start_date <= duration < end_date