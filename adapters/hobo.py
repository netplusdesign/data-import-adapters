"""
    Read temperature data from Hoboware CSV export
    See https://www.onsetcomp.com/products/data-loggers-sensors/temperature/
"""
from adapters.adapter import Adapter

class Hobo(Adapter):

    def __init__(self, config):

        super().__init__(config)

        # skip header row retuned with Hobo CSV format
        self._skip = 2
