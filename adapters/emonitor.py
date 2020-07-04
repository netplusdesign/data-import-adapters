"""
    Read energy data from Powerhouse Dynamics eMonitor CSV files circa 2012-2014
"""
from adapters.adapter import Adapter

class EMonitor(Adapter):

    def __init__(self, config):

        super().__init__(config)

        # skip header row retuned with eMonitor CSV format
        self._skip = 7
