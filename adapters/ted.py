"""
    Read energy data from The Energy Detective (TED) CSV files circa 2012
"""
import csv
from adapters.adapter import Adapter

class TED(Adapter):
    '''  '''

    def __init__(self, config):

        super().__init__(config)

        # skip header row retuned with TED CSV format
        self._skip = 0