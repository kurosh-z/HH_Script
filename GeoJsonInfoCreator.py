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

    def dump(self):
        with open(self.GEOJSONINFO_PATH, "w") as f:
            json.dump(self.geoJsonInfo, f)
        logger.info("geoJsonInfo sucessfully dumped in : {}".format(self.GEOJSONINFO_PATH))
