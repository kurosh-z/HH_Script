import json
import sys
import logging

logger = logging.getLogger(__name__)


class GeoJsonInfoCreator(object):
    """Singelton Calass which generates log file for analysed data to be used in javascript
    Args:
        logPath (String): path to the log template or existing log
        forceCreate (boolean): force creating new json file

    """

    GEOJSONINFO_PATH = "/var/www/html/hhmaps/HH/geoJsonInfo.json"

    def init(self, *args, **kwargs):
        try:
            with open(self.GEOJSONINFO_PATH, "r") as f:
                print("geoJsonInfo opened")
                self.geoJsonInfo = json.load(f)

        except:
            with open(self.GEOJSONINFO_PATH, "w") as f:
                self.geoJsonInfo = {}
                json.dump(self.geoJsonInfo, f)
                print("geoJsonInfo created")
                logger.info("new geoJsonInfo created in : {}".format(self.GEOJSONINFO_PATH))
        f.close()

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def add_Exceptions(self, logFileName, gas=None):
        exceptions = []
        gasList = ["SO2", "NO2", "O3"]
        if gas:
            gasList = [gas]
        thresholds = ["50", "75"]
        if not gas:
            logger.warning(" The log file has less than 10 entries: {}".format(logFileName))

        for gas in gasList:
            logger.warning(" There is no valid value for gas {} log file: {} ".format(gas, logFileName))
            for threshold in thresholds:
                exceptionName = logFileName.split(".")[0] + "-" + gas + "-" + threshold
                exceptions.append(exceptionName)

        if "EXCEPTIONS" in self.geoJsonInfo:
            self.geoJsonInfo["EXCEPTIONS"].extend(exceptions)
        else:
            self.geoJsonInfo["EXCEPTIONS"] = exceptions

    def is_already_done(self, logFileName):

        if not "EXCEPTIONS" in self.geoJsonInfo:
            self.geoJsonInfo["EXCEPTIONS"] = []

        gasList = ["SO2", "NO2", "O3"]
        thresholds = ["50", "75"]
        for gas in gasList:
            for threshold in thresholds:
                exceptionName = logFileName.split(".")[0] + "-" + gas + "-" + threshold
                if not exceptionName in self.geoJsonInfo["EXCEPTIONS"] and not exceptionName in self.geoJsonInfo:
                    return False

        return True

    def dump(self):
        with open(self.GEOJSONINFO_PATH, "w") as f:
            json.dump(self.geoJsonInfo, f)
        logger.info("geoJsonInfo sucessfully dumped in : {}".format(self.GEOJSONINFO_PATH))
