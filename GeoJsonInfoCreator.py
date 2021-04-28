import json
import sys
import logging

logger = logging.getLogger(__name__)

GEOJSONINFO_HH_PATH = "/var/www/html/hhmaps/HH/geoJsonInfoHH.json"
GEOJSONINFO_HL_PATH = "/var/www/html/hhmaps/HL/geoJsonInfoHL.json"


class GeoJsonInfoCreator(object):
    """Singelton Calass which generates log file for analysed data to be used in javascript
    Args:
        logPath (String): path to the log template or existing log
        forceCreate (boolean): force creating new json file

    """

    def init(self, *args, **kwargs):
        self.path = ""

        if args[0] == "HH":
            self.path = GEOJSONINFO_HH_PATH
        elif args[0] == "HL":
            self.path = GEOJSONINFO_HL_PATH
        else:
            raise Exception('expected to recieve HH or HL as argument got:"{}"'.format(args[0]))

        try:
            with open(self.path, "r") as f:
                print("geoJsonInfo opened")
                self.geoJsonInfo = json.load(f)

        except:
            with open(self.path, "w") as f:
                self.geoJsonInfo = {}
                json.dump(self.geoJsonInfo, f)
                logger.info("new geoJsonInfo created in : {}".format(self.path))
        f.close()

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    # def add_Exceptions(self, logFileName, logType, gas=None, errMsg=None,):
    def add_Exceptions(self, **kwargs):
        logType = kwargs.get("logType")
        logFileName = kwargs.get("logFileName")
        gas = kwargs.get("gas", None)
        errMsg = kwargs.get("errMsg")

        exceptions = []
        gasList = []
        thresholds = ["50", "75"]
        if gas:
            gasList = [gas]
        else:
            gasList = ["SO2", "NO2", "O3"] if logType == "HH" else ["H2S", "NO2", "O3", "SO2"]
            logger.warning("there is a problem with log file {} - details: \r\n {}".format(logFileName, errMsg))

        for gas in gasList:
            if not gas and not errMsg:
                logger.warning(" There is no valid value for gas {} log file: {} ".format(gas, logFileName))
            for threshold in thresholds:
                exceptionName = logFileName.split(".")[0] + "-" + gas + "-" + threshold
                exceptions.append(exceptionName)

        if "EXCEPTIONS" in self.geoJsonInfo:
            self.geoJsonInfo["EXCEPTIONS"].extend(exceptions)
        else:
            self.geoJsonInfo["EXCEPTIONS"] = exceptions

    def is_already_done(self, logFileName, logType):

        if not "EXCEPTIONS" in self.geoJsonInfo:
            self.geoJsonInfo["EXCEPTIONS"] = []

        gasList = ["SO2", "NO2", "O3"] if (logType == "HH") else ["H2S", "NO2", "O3", "SO2"]
        thresholds = ["50", "75"]
        for gas in gasList:
            for threshold in thresholds:
                exceptionName = logFileName.split(".")[0] + "-" + gas + "-" + threshold
                if not exceptionName in self.geoJsonInfo["EXCEPTIONS"] and not exceptionName in self.geoJsonInfo:
                    return False

        return True

    def dump(self):
        with open(self.path, "w") as f:
            json.dump(self.geoJsonInfo, f)
        logger.info("geoJsonInfo sucessfully dumped in : {}".format(self.path))
