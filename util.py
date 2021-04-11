import os
import csv
import json
import numpy as np
import pandas as pd
import logging
logger = logging.getLogger(__name__)
# logging.basicConfig(filename='createGeoJson.log', filemode='w',
#                     format='%(asctime)s - %(message)s', level=logging.INFO)
########################################################################
#                     General Utility Functions
########################################################################

PROPERTIES= ['type', 'date', 'time', 'sensor_mode', 'alarm_state',
               'gas_value', 'unit', 'temprature',
              'latitude', 'longitude', 'GPS_time']

def fileList(path, ending=None, ScanSubFolder=False):
    """[returns the list of all files in a path]

    Args:
        pathlist (List): [list of the path, in which files should be
        listed]
        ending ([String], optional): [only search files with an
        specific ending]. Defaults to None.
        SubFolder: if True search also one layer deeper in Folder
    Return:
       List of all file in folder (if subfolder is True also returns 
                                    path for the files)
    """
    files = []
    path_list = []
    if ending is None:
        files = [f for f in os.listdir(path)]
        path_list = [path for _ in files]
    else:
        files = [f for f in os.listdir(path) if f.endswith(ending)]
        path_list = [path for _ in files]
    # performe one layer subfolder search if ScanSubFolder is True
    if(ScanSubFolder):
        subfolders = [f.path for f in os.scandir(path) if f.is_dir()]
        for subf in subfolders:
            subFiles = fileList(subf, ending, False)
            files.extend(subFiles)
            sub_path_list = [subf for _ in subFiles]
            path_list.extend(sub_path_list)
        # if subFolders is True, returns also path of the files
        return files, path_list

    return files


def logToCsv(logPath, logName, savePath):
    """ Save log files as csv 

    Args:
        logPath (String): path for the log file 
        logName (String): file name (with extension .log)
        savePath (String): path to save csv file
    """
    logText = open(os.path.join(logPath, logName), "r")

    # check if the savePath already exist otherwise create it
    if not os.path.exists(savePath):
        os.mkdir(savePath)
        # print('directory created for saving csv files: {}'.format(savePath))
        logger.info(
            'directory created for saving csv files: {}'.format(savePath))

    # change the extension to csv
    csvName = logName.split('.')[0] + '.csv'
    # create csv file
    # print('csv pathName: ' + os.path.join(savePath, csvName))
    with open(os.path.join(savePath, csvName), 'w') as csvFile:
        writer = csv.writer(csvFile)
        for line in logText.readlines():
            writer.writerow(line.split(' '))
    csvFile.close()


def generate_csv_name(logFileName):
    """generate appropraite name for csv files
       (to make sure that the naming convention holds for all
        the files you should use this for generating name)
    Args:
        logFileName (String): name of the original log file

    Returns:
        [String]: name for the csv file
    """
    return logFileName.split('.')[0] + '.csv'


def generate_geogjosn_name(logFileName, gasType, percentage):
    """generate appropraite name for geojson files
       (to make sure that the naming convention holds for all
        the files you should use this for generating name)
    Args:
        logFileName (String): name of the original log file
        gasType (String): type of gas (NO2, O3, SO2)
        percentage (Number): percentage used in data analyis (50 or 75)
    Returns:
        [String]: name for the geogjon file
    """
    per = ''
    con1 = percentage == 50
    con2 = percentage == 75
    if (con1):
        per = '-50'
    if (con2):
        per = '-75'
    if(not (con1 or con2)):
        raise Exception('expected 50 or 75 got :{}'.format(percentage))
    return logFileName.split('.')[0] + '-' + gasType + per

def create_gasInfo_path(path):
    """creates path to be used in gasInfo (look at AnalyseHH.py)

    Args:
        path (string): original path with /var/www/html/path/to/

    Returns:
        path [string]: return the path aftar => /path/to
    """
    splitted = path.split('/')
    index=1.5
    for idx, el in enumerate(splitted):
        if(el == 'html'):
            index = idx+1
            break
    
    if(isinstance(index, int)):
        return '/'+ '/'.join(splitted[index: len(splitted)])
    else:
        raise Exception('expected a path in /var/www/html got: "{}"'.format(path))       
    
    
def is_geogjson_exist(gPath, gName):
    # if the gPath dosesn't exist yet return false
    if not os.path.exists(gPath):
        return False
    else:
        # generate all the geogson files in path
        geoList = fileList(gPath, '.geojson')
        for g in geoList:
            if (g == gName + '.geojson'):
                return True
    return False


def plot_line(ax, x_line, y_line):
    ax.plot(x_line, y_line)


def remove_csv_file(path, fileName):
    """removes csv files 
       for security reasons it checks if the extension is csv

    Args:
        path (String): path for the csv file
        fileName (String): name of the file (with extension)
    """

    if (fileName.split('.')[-1] == 'csv'):
        os.remove(os.path.join(path, fileName))
    else:
        raise Exception(
            'expected a file with extension .csv but recieved:{}'.format(fileName))


def df_filter(df, gasType):
    """returns a filtered pandas dataframe according to gasType 
        and Validity of GPS and drop the NaN or inf values


    Args:
        df (pandas dataframe): dataframe to be filtered
        gasType (String): gas type which new dataframe generated for
    """
    df[["latitude", "longitude"]] = df[["latitude", "longitude"]].apply(pd.to_numeric, errors='coerce')
    return df.query('type == "{}" & GPS_position_validity_mode != 0 & gas_value != inf  & @pd.notna(gas_value) & @pd.notna(latitude) & @pd.notna(longitude)'.format(gasType))


def df_to_geojson(df, properties, extraProps):
    """Returns a geojson file from pandas dataframe

    Args:
        df (pandas dataframe): dataframe to extract properties from
        properties (list String): list of properties to include in geojson object
        extraProps (dictionary): extra features to be added which are not inlude
                                 in df

    Returns:
        [geojson object]: geojson object from df
    """
    geojson = {'type': 'FeatureCollection', 'features': []}
    for _, row in df.iterrows():
        feature = {'type': 'Feature',
                   'properties': {},
                   'geometry': {'type': 'Point',
                                'coordinates': []}}
        # add properties from df
        feature['geometry']['coordinates'] = [
            row['longitude'], row['latitude']]
        for prop in properties:
            if(prop in PROPERTIES):
                feature['properties'][prop] = row[prop]
        # add extra properties
        for key, value in extraProps.items():
            feature['properties'][key] = value
        # append features
        geojson['features'].append(feature)

    return geojson


def dump_geojson(geojson, path, fileName):
    """dump geojson data 

    Args:
        geojson (geojson object): geojson to be dumped
        path (String): path for dumping file
        fileName (String): name of the file (without extension!)

    """

    if not os.path.exists(path):
        os.mkdir(path)
        # print('directory created for saving geojson file: {}'.format(path))
        logger.info(
            'directory created for saving geojson file: {}'.format(path))

    with open(os.path.join(path, fileName + '.geojson'), 'w') as f:
        json.dump(geojson, f)
        f.close()
    # print('file": {} " sucessfully saved in: "{}"'.format(
    #     fileName + '.geojson', path))
    logger.info('file": {} " sucessfully saved in: "{}"'.format(
        fileName + '.geojson', path))
