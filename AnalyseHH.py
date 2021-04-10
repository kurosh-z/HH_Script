import os
import pandas as pandas
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from util import df_filter, plot_line, df_to_geojson, dump_geojson, generate_geogjosn_name
from Filelogger import Filelogger


class AnalyseHH:
    """ class to analyse HH Data
        Contructor Args:

            name (String): name of the object
            df (pandas dataframe):  dataframe contianing gas data
            gas (String):  the gas to be analysed
    """
    # INFOLOGGER_PATH = '/var/www/html/hhmaps/HH/available_geojsons.json'
    INFOLOGGER_PATH = '/Users/kurosh/Documents/Draeger/HHData/available_geojsons.json'
    file_logger = Filelogger(INFOLOGGER_PATH)

    def __init__(self, logFileName, df, gas):
        self.logFileName = logFileName
        self.df = df
        self.gas = gas
        self.df_filtered = df_filter(df, gas)
        self.values = self.df_filtered['gas_value'].abs()

        # if there is any value continue
        if(len(self.values)):
            self.max = self.values.max()
            self.min = self.values.min()
            self.mean = self.values.mean()
            self.distMaxMean = self.max - self.mean
            self.quarter_dist = self.distMaxMean / 4.0
 
            # thresholds
            self.threshold50 = self.mean + 2 * self.quarter_dist
            self.threshold75 = self.mean + 3 * self.quarter_dist
            self.df50 = self.df_filtered.query(
                'gas_value > {}'.format(self.threshold50))
            self.df75 = self.df_filtered.query(
                'gas_value > {}'.format(self.threshold75))
            self.VALUE_FLAG = False

        else:
            self.VALUE_FLAG = True

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

    def create_geojsons(self):
        # extra features to be added:
        extra_features = {'max_day_val': self.max,
                          'min_day_val': self.mean, 'mean_day_val': self.mean}

        # create geojson files
        self.geojson50 = df_to_geojson(
            self.df50, self.df50.columns, extra_features)
        self.geojson75 = df_to_geojson(
            self.df75, self.df75.columns, extra_features)

    def dump_geojsons(self, path):
        # fileName = self.logFileName.split('.')[0] + '_' + self.gas + '_50'
        fileName = generate_geogjosn_name(self.logFileName, self.gas, 50)
        dump_geojson(self.geojson50, path, fileName)
        self.add_to_loggfile(path, fileName)

        # fileName = self.logFileName.split('.')[0] + '_' + self.gas + '_75'
        fileName = generate_geogjosn_name(self.logFileName, self.gas, 75)
        dump_geojson(self.geojson75, path, fileName)
        self.add_to_loggfile(path, fileName)

    def add_to_loggfile(self, path, fileName):

        # general format of the fileName is like HH1-11012021_O3_50.geojson
        # extract infos from fileName
        fullPath = os.path.join(path, fileName+'.geojson')
        name = fileName.split('.')[0]
        splitted = name.split('_')
        hhtype = splitted[0].split('-')[0]
        gas = splitted[1]
        percentage = splitted[2]
        date = splitted[0].split('-')[1]
        date = date[0:2] + '-' + date[2:4] + '-' + date[4:8]
        gasInfo = {
            "path": fullPath,
            "percentage": percentage,
            "fileName": fileName,
        },
        self.file_logger.add_new_gasInfo(date, gas, gasInfo, hhtype)

    def finalize(self):
        self.file_logger.dump_geojson()