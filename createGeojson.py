import os
import logging
import datetime
import pandas as pd
import numpy as np
from AnalyseHH import AnalyseHH
from GeoJsonInfoCreator import GeoJsonInfoCreator

from util import (
    fileList,
    is_geogjson_exist,
    logToCsv,
    remove_csv_file,
    generate_csv_name,
    generate_geogjosn_name,
    csvToDataFrame,
    is_logFile_for_today,
)


def main():
    gjInfo = GeoJsonInfoCreator()

    # logsToBeAnalysed = [
    #     {
    #         "logPath": "/Users/kurosh/Documents/Draeger/HHData/HH_Data/2020",
    #         "geoJsonPath": "/var/www/html/hhmaps/HH/2020_Geojson",
    #     },
    #     {
    #         "logPath": "/Users/kurosh/Documents/Draeger/HHData/HH_Data/HH1",
    #         "geoJsonPath": "/var/www/html/hhmaps/HH/HH1_Geojson",
    #     },
    #     {
    #         "logPath": "/Users/kurosh/Documents/Draeger/HHData/HH_Data/HH2",
    #         "geoJsonPath": "/var/www/html/hhmaps/HH/HH2_Geojson",
    #     },
    # ]
    logsToBeAnalysed = [
        {"logPath": "/var/www/html/HH_Data/2020", "geoJsonPath": "/var/www/html/hhmaps/HH/2020_Geojson"},
        {"logPath": "/var/www/html/HH_Data/HH1", "geoJsonPath": "/var/www/html/hhmaps/HH/HH1_Geojson"},
        {"logPath": "/var/www/html/HH_Data/HH2", "geoJsonPath": "/var/www/html/hhmaps/HH/HH2_Geojson"},
        {"logPath": "/var/www/html/HH_Data/HH3", "geoJsonPath": "/var/www/html/hhmaps/HH/HH3_Geojson"},
        {"logPath": "/var/www/html/HH_Data/HH4", "geoJsonPath": "/var/www/html/hhmaps/HH/HH4_Geojson"},
    ]

    gasList = ["SO2", "NO2", "O3"]
    # load exception list (files which already analysed and after filtering had no valid data in them )
    # exceptions = load_exeptions()

    for log_geoJson in logsToBeAnalysed:
        logPath = log_geoJson["logPath"]
        geoJsonPath = log_geoJson["geoJsonPath"]
        loglist, dir_list = fileList(logPath, ".log", True)
        log_dir_list = list(zip(loglist, dir_list))

        for log_dir_tupel in log_dir_list:
            # check if the file already exist its enought to just check for one gas with 50%
            logFileName = log_dir_tupel[0]
            logFilePath = log_dir_tupel[1]
            gName = generate_geogjosn_name(logFileName, "SO2", 50)

            if not gjInfo.is_already_done(logFileName):
                # convert log files to a temporary csv
                numColumns = logToCsv(logFilePath, logFileName, geoJsonPath)
                if numColumns == "EMPTY":
                    # exceptions = add_empty_file_to_exceptions(exceptions, logFileName)
                    gjInfo.add_Exceptions(logFileName)
                else:
                    # csvName = logFileName.split('.')[0] + '.csv'
                    csvName = generate_csv_name(logFileName)
                    # open csv with pandas:
                    df = csvToDataFrame(geoJsonPath, csvName, numColumns)
                    for gas in gasList:
                        gas_analyse = AnalyseHH(logFileName, df, gas)
                        if gas_analyse.VALUE_FLAG:
                            gjInfo.add_Exceptions(logFileName, gas)
                        else:
                            gas_analyse.create_geojsons()
                            gas_analyse.dump_geojsons(geoJsonPath)

                # analyse_data(df, logFileName, geoJsonPath)
                # remove temp csv file
                remove_csv_file(geoJsonPath, csvName)

    # dump json file to be used in javascript
    # AnalyseHH.geoLogger.dump_log()

    gjInfo.dump()


##################################################################################
if __name__ == "__main__":
    loggingName = "createGeoJson_"
    dt = datetime.datetime.now()
    dt = str(dt).replace(":", "-")
    dt = dt.replace(" ", "_")
    loggingName += dt + ".log"
    loggingName = "/Users/kurosh/Documents/Draeger/HHData/HH_Script/log/" + loggingName
    # loggingName = "/var/www/html/HH_Script/log/" + loggingName

    logging.basicConfig(
        filename=loggingName,
        filemode="w",
        format="%(asctime)s - %(message)s",
        level=logging.INFO,
    )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter("%(levelname)s : %(message)s")
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    # call main function

    main()
