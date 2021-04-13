import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from numpy import abs as npabs
from util import (
    df_filter,
    plot_line,
    df_to_geojson,
    dump_geojson,
    generate_geogjosn_name,
    create_gasInfo_path,
    chooseRandIndices,
)
from GeoJsonInfoCreator import GeoJsonInfoCreator

# from Geologger import Geologger
EPSILON = 1e-6


class AnalyseHH:
    """class to analyse HH Data
    Contructor Args:

        name (String): name of the object
        df (pandas dataframe):  dataframe contianing gas data
        gas (String):  the gas to be analysed
    """

    # INFOLOGGER_PATH = "/var/www/html/hhmaps/HH/geoJsonInfo.json"
    # INFOLOGGER_PATH ='/Users/kurosh/Documents/Draeger/HHData/geoJsonInfo.json'
    # geoLogger = Geologger(INFOLOGGER_PATH, True)
    gjInfoCreator = GeoJsonInfoCreator()

    def __init__(self, logFileName, df, gas):
        self.logFileName = logFileName
        self.df = df
        self.gas = gas
        self.df_filtered = df_filter(df, gas)
        self.values = self.df_filtered["gas_value"].abs()
        # print("analysing gas: {} from logfile: {}".format(gas, logFileName))
        # if there is any value continue
        if len(self.values):
            self.max = self.values.max()
            self.min = self.values.min()
            self.mean = self.values.mean()
            self.distMaxMean = self.max - self.mean
            self.quarter_dist = self.distMaxMean / 4.0

            # thresholds
            self.threshold50 = self.mean + 2 * self.quarter_dist
            self.threshold75 = self.mean + 3 * self.quarter_dist
            ## EPSILON in the next line is to prevent numerical issues for the very rare case of all the values being the same
            self.df50 = self.df_filtered.query("@npabs(gas_value) >= {}".format(self.threshold50 - EPSILON))
            self.df75 = self.df_filtered.query("@npabs(gas_value) >= {}".format(self.threshold75 - EPSILON))
            self.rndIndices75 = chooseRandIndices(self.df75["gas_value"])
            self.rndIndices50 = chooseRandIndices(self.df50["gas_value"])
            self.VALUE_FLAG = False

        else:
            self.VALUE_FLAG = True

    def geoJson_add_entery(self, path, fileName):
        # general format of the fileName is like HH1-11012021_O3_50.geojson
        # extract infos from fileName
        # we don't need a fullpath just after www/html/

        # fullPath = os.path.join(path, fileName+'.geojson')
        _path = create_gasInfo_path(path)
        fullPath = os.path.join(_path, fileName + ".geojson")
        name = fileName.split(".")[0]
        self.gjInfoCreator.geoJsonInfo[name] = fullPath

    def plot_distribution(self):

        c_bins = np.linspace(0, self.max, 40)
        fig, ax = plt.subplots(tight_layout=True)

        # N is the count in each bin, bins is the lower-limit of the bin
        N, bins, patches = ax.hist(self.values, bins=300)

        # We'll color code by height, but you could use any scalar
        fracs = N / N.max()

        # we need to normalize the data to 0.1 for the full range of the colormap
        norm = colors.Normalize(fracs.min(), fracs.max())

        # Now, we'll loop through our objects and set the color of each accordingly
        for thisfrac, thispatch in zip(fracs, patches):
            color = plt.cm.viridis(norm(thisfrac))
            thispatch.set_facecolor(color)

        y_line = np.linspace(0, N.max(), 10)
        for i in range(0, 5):
            x_line = np.ones(len(y_line)) * (self.quarter_dist * i + self.mean)
            plot_line(ax, x_line, y_line)

        plt.show()
        return [fig, ax]

    def create_geojsons(self):
        # extra features to be added:
        extra_features = {"max_day_val": self.max, "min_day_val": self.mean, "mean_day_val": self.mean}

        # create geojson files
        #  ah.df50[ah.df50.index.isin(ah.rndIndices75)]
        # we are going to add just random selected point in df50 or df75
        rndPoints50 = self.df50[self.df50.index.isin(self.rndIndices50)]
        rndPoints75 = self.df75[self.df75.index.isin(self.rndIndices75)]
        self.geojson50 = df_to_geojson(rndPoints50, self.df50.columns, extra_features)
        self.geojson75 = df_to_geojson(rndPoints75, self.df75.columns, extra_features)

    def dump_geojsons(self, path):
        # fileName = self.logFileName.split('.')[0] + '_' + self.gas + '_50'
        fileName = generate_geogjosn_name(self.logFileName, self.gas, 50)
        dump_geojson(self.geojson50, path, fileName)
        # self.add_to_loggfile(path, fileName)
        self.geoJson_add_entery(path, fileName)

        # fileName = self.logFileName.split('.')[0] + '_' + self.gas + '_75'
        fileName = generate_geogjosn_name(self.logFileName, self.gas, 75)
        dump_geojson(self.geojson75, path, fileName)
        # self.add_to_loggfile(path, fileName)
        self.geoJson_add_entery(path, fileName)

    def add_to_loggfile(self, path, fileName):

        # general format of the fileName is like HH1-11012021_O3_50.geojson
        # extract infos from fileName
        # we don't need a fullpath just after www/html/

        # fullPath = os.path.join(path, fileName+'.geojson')
        _path = create_gasInfo_path(path)
        fullPath = os.path.join(_path, fileName + ".geojson")
        name = fileName.split(".")[0]
        splitted = name.split("-")
        hhtype = splitted[0]
        date = splitted[1]
        gas = splitted[2]
        percentage = splitted[3]
        date = date[0:2] + "-" + date[2:4] + "-" + date[4:8]
        gasInfo = (
            {
                "path": fullPath,
                "percentage": percentage,
                "fileName": fileName,
            },
        )
        self.geoLogger.add_new_gasInfo(date, gas, gasInfo, hhtype)

    # def finalize(self):
    #     self.geoLogger.dump_geojson()


# if __name__ == "__main__":
#     # TESTING
#     from util import logToCsv, csvToDataFrame

#     logFileName = "HH1-10022021.log"
#     csvName = "HH1-10022021.csv"
#     logPath = "/Users/kurosh/Documents/Draeger/HHData/HH_Data/HH1/02/"
#     csvPath = "/Users/kurosh/Documents/Draeger/HHData/test/"
#     geoJsonPath = "/var/www/html/hhmaps/HH/HH1_Geojson"
#     numColumns = logToCsv(logPath, logFileName, csvPath)
#     df = csvToDataFrame(csvPath, csvName, numColumns)
#     ah = AnalyseHH(logFileName, df, "SO2")
#     if not ah.VALUE_FLAG:
#         print(ah.max)
#         print(ah.min)
#         print(ah.mean)
#         print(ah.threshold75)
#         print(ah.threshold50)
#         ah.create_geojsons()
#         ah.dump_geojsons(geoJsonPath)
#         gjInfoCreator = GeoJsonInfoCreator()
#         gjInfoCreator.dump()
#     else:
#         print("value flag is true!")
