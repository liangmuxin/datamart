from datamart.materializers.materializer_base import MaterializerBase

import pandas as pd
import typing
import os
import sys
import traceback
import datetime
import shutil
from datamart.materializers.tradingeconomics_downloader.file_downloader import FileDownloader


class TradingEconomicsMaterializer(MaterializerBase):
    """TradingEconomicsMaterializer class extended from  Materializer class

    """

    def __init__(self):
        """ initialization and loading the city name to city id map

        """
        MaterializerBase.__init__(self)
        self.key = None

    def get(self,
            metadata: dict = None,
            variables: typing.List[int] = None,
            constrains: dict = None
            ) -> typing.Optional[pd.DataFrame]:
        """ API for get a dataframe.

            Args:
                metadata: json schema for data_type
                variables:
                constrains: include some constrains like date_range, location and so on

                Assuming date is in the format %Y-%m-%d
        """
        if not constrains:
            constrains = dict()

        materialization_arguments = metadata["materialization"].get("arguments", {})
        getUrl = metadata['url']
        if "key" in constrains:
            self.key = {"key": constrains["key"]}
        else:
            self.headers = {"key": "guest:guest"}
        date_range = constrains.get("date_range", {})
        datestr=""
        now = datetime.datetime.now()

        if "start" in date_range and date_range["start"]:
            datestr += date_range["start"]
        else:
            datestr += "{}-{}-{}".format(now.year-1, "01", "01")
        if "end" in date_range and date_range["end"]:
            datestr += '/'+date_range["end"]
        else:
            datestr += '/' + "{}-{}-{}".format(now.year, "01", "01")
        path1, path2=getUrl.split("?c=")
        getUrl=path1+"/"+datestr+"?c="+path2
        if "locations" in constrains:
            locations = constrains["locations"]
            getUrl=getUrl.replace("all",",".join([x.replace(' ', '%20') for x in locations]))

        datasetConfig = {
            "where_to_download": {
                "frequency": "quarterly",
                "method": "get",
                "file_type": "csv",
                "template": metadata['url'],
                "replication": {
                },
                "identifier": metadata['title'].replace(' ', '_')
            },
        }

        return self.fetch_data(getUrl, datasetConfig)

    def fetch_data(self, getUrl, datasetConfig):
        """
        Returns:
             result: A pd.DataFrame;
        """
        try:
            data = pd.read_csv(getUrl, encoding='utf-16')
            return data
        except Exception as e:
            print('exception in run', e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            print(''.join(lines))