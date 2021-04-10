
import os
import pandas as pd
from util import fileList, is_geogjson_exist, logToCsv, remove_csv_file, generate_csv_name, generate_geogjosn_name
from AnalyseHH import AnalyseHH
import logging
import datetime


def main():

    header = ['type', 'bt_MAC', 'date', 'time', 'sensor_mode', 'alarm_state',
              'battery_state', 'measurement_unit_channel_code',
              'measurement_unit_channel_number', 'gas_value', 'unit', 'temprature',
              'latitude', 'longitude', 'GPS_time', 'GPS_speed',
              'GPS_position_validity_mode', 'number_of_visible_GPS_satelite']

    # logPath = '/Users/kurosh/Documents/Draeger/HHData/HH1'
    # geoJsonPath = '/Users/kurosh/Documents/Draeger/HHData/HH1_Geojson'

    # loglist = fileList(logPath, '.log')

    logsToBeAnalysed = [
        {
            'logPath': '/Users/kurosh/Documents/Draeger/HHData/HH1',
            'geoJsonPath': '/var/www/html/hhmaps/HH/HH1_Geojson'
        },
        {
            'logPath': '/Users/kurosh/Documents/Draeger/HHData/HH2',
            'geoJsonPath': '/var/www/html/hhmaps/HH/HH2_Geojson'
        }
    ]

    for log_geoJson in logsToBeAnalysed:
        logPath = log_geoJson['logPath']
        geoJsonPath = log_geoJson['geoJsonPath']
        loglist, dir_list = fileList(logPath, '.log', True)
        log_dir_list = list(zip(loglist, dir_list))

        for log_dir_tupel in log_dir_list:
            # check if the file already exist its enought to just check for one gas with 50%
            logFileName = log_dir_tupel[0]
            logFilePath = log_dir_tupel[1]
            gName = generate_geogjosn_name(logFileName, 'SO2', 50)
            # if the file dosen't exist do the analysis
            if(not is_geogjson_exist(geoJsonPath, gName)):
                # convert log files to a temporary csv
                logToCsv(logFilePath, logFileName, geoJsonPath)
                # csvName = logFileName.split('.')[0] + '.csv'
                csvName = generate_csv_name(logFileName)
                # open csv with pandas:
                df = pd.read_csv(os.path.join(
                    geoJsonPath, csvName), names=header, low_memory=False)
                analyse_data(df, logFileName, geoJsonPath)
                # remove temp csv file
                remove_csv_file(geoJsonPath, csvName)

    # dump log file to be used in javascript
    AnalyseHH.file_logger.dump_log()


def analyse_data(df, logFileName, geoJsonPath):
    # gasList = ['SO2', 'NO2', 'O3']
    gasList = ['SO2', 'NO2', 'O3']
    for gas in gasList:
        gas_analyse = AnalyseHH(logFileName, df, gas)
        # gas_analyse.plot_distribution()
        # if value is empty do nothing!
        if(gas_analyse.VALUE_FLAG):
            print('WARNING: There is no valid value for log file: {} '.format(
                logFileName))
            logging.info('WARNING: There is no valid value for log file: {} '.format(
                logFileName))
        else:
            gas_analyse.create_geojsons()
            gas_analyse.dump_geojsons(geoJsonPath)


##################################################################################
if __name__ == '__main__':
    loggingName = 'createGeoJson_'
    dt = datetime.datetime.now()
    dt = str(dt).replace(":", '-')
    dt.replace(" ", "")
    loggingName += dt+'.log'
    loggingName = '/Users/kurosh/Documents/Draeger/HHData/HH_Script/log/' + loggingName

    logging.basicConfig(filename=loggingName, filemode='w',
                        format='%(asctime)s - %(message)s', level=logging.INFO)
    # call main function
    main()

    # logsToBeAnalysed = [
    #     {
    #         'logPath': '/ var/www/html/HH_Data/HH1,
    #         'geoJsonPath': '/var/www/html/hhmaps/HH/HH1_Geojson'
    #     },
    #     {
    #         'logPath': '/var/www/html/HH_Data/HH2',
    #         'geoJsonPath': '/var/www/html/hhmaps/HH/HH2_Geojson'
    #     }
    # ]