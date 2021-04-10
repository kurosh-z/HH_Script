import json


class Filelogger(object):
    """Singelton Calass which generates log file for analysed data to be used in javascript
        Args:
            logPath (String): path to the log template or existing log
    """

    def init(self, logPath, *args, **kwargs):

        self.logPath = logPath
        with open(logPath, 'r') as f:
            logJSON = json.load(f)
        self.logJSON = logJSON

    def __new__(cls, *args, **kwds):
        it = cls.__dict__.get("__it__")
        if it is not None:
            return it
        cls.__it__ = it = object.__new__(cls)
        it.init(*args, **kwds)
        return it

    def generate_date_list(self, hhtype):
        dates = [self.logJSON[hhtype][i]['date']
                 for i in range(len(self.logJSON[hhtype]))]
        return dates

    def is_date_exist(self, date, hhtype):
        date_list = self.generate_date_list(hhtype)
        for index, item in enumerate(self.logJSON[hhtype]):
            if (item['date'] == date):
                return (True, index)
        return (False, -1)

    # create a new date entry
    def add_new_date_entry(self, date, hhtype):
        self.logJSON[hhtype].append({'date': date, 'data': []})

    def list_all_gas_in_day(self, date, hhtype):
        exist, index = self.is_date_exist(date,  hhtype)
        all_data_in_day = self.logJSON[hhtype][index]['data']
        return [item['gas'] for item in all_data_in_day]

    def list_all_gas_in_day(self, date, hhtype):
        exist, index = self.is_date_exist(date, hhtype)
        all_data_in_day = self.logJSON[hhtype][index]['data']
        return [item['gas'] for item in all_data_in_day]

    def is_gas_exist_in_day(self, data, gas, hhtype):
        all_gas = self.list_all_gas_in_day(data, hhtype)
        for index, item in enumerate(all_gas):
            if(item == gas):
                return (True, index)
        return (False, -1)

    def add_new_gas_entry(self, date, gas, hhtype):
        # get index of the date
        date_exist, dateIndex = self.is_date_exist(date, hhtype)
        if(not date_exist):
            raise Exception(
                'the date: "{}" ,which you want to add gas entry does not exist!'.format(date))
        self.logJSON[hhtype][dateIndex]['data'].append(
            {'gas': gas, 'gasInfo': []})

    def list_all_fileName_in_gasInfo(self, date, gas, hhtype):
        date_exist, dateIndex = self.is_date_exist(date, hhtype)  # :
        # :
        gas_exist, gasIndex = self.is_gas_exist_in_day(date, gas, hhtype)
        if(not date_exist):
            raise Exception(
                'there exist no date: "{}" ,in which you want to list all fileNames!'.format(date))
        if(not gas_exist):
            raise Exception(
                'there exist no gas: "{}" in day "{}",in which you want to list fileNames!'.format(gas, date))
        return [item['fileName'] for item in self.logJSON[hhtype][dateIndex]['data'][gasIndex]['gasInfo']]

    def is_gasInfo_exist_for_fileName(self, date, gas, fileName, hhtype):
        all_fileNames = self.list_all_fileName_in_gasInfo(date, gas, hhtype)
        for index, item in enumerate(all_fileNames):
            if(fileName == item):
                return (True, index)
        return (False, -1)

    def add_new_gasInfo(self, date, gas, gasInfo, hhtype):
        """add new gasInfo to the logJSON

        Args:
            date (String): Date of the gasInfo
            gas (String):  Gas Type one of (NO2, O3, SO2)
            gasInfo (dict): dict containing {path: String, percentage: String, fileName:String}
            hhtype (String): one of (HH1, HH2, HH3)
        """
        date_exist, dateIndex = self.is_date_exist(date, hhtype)
        if(not date_exist):
            self.add_new_date_entry(date, hhtype)
            date_exist, dateIndex = self.is_date_exist(date, hhtype)

        gas_exist, gasIndex = self.is_gas_exist_in_day(date, gas, hhtype)
        if(not gas_exist):
            self.add_new_gas_entry(date, gas, hhtype)
            gas_exist, gasIndex = self.is_gas_exist_in_day(date, gas, hhtype)

        self.logJSON[hhtype][dateIndex]['data'][gasIndex]['gasInfo'].append(
            gasInfo)
        #     {'gas': gas, 'gasInfo': []})

    def dump_log(self):
        with open(self.logPath, "w") as write_file:
            json.dump(self.logJSON, write_file)
        print('log file sucessfully dumped in: "{}"'.format(self.logPath))

# if (__name__ == '__main__'):
#     alog = ALog('/Users/kurosh/Documents/Draeger/HHData/testlog.json')
#     date_list = alog.generate_date_list('h1')
#     date_exist, dateIndex = alog.is_date_exist(date_list[1], 'h1')
#     alog.add_new_date_entry('03-01-2021', 'h1')
#     all_gas = alog.list_all_gas_in_day('02-01-2020', 'h1')
#     all_gas2 = alog.list_all_gas_in_day('03-01-2021', 'h1')

#     all_gas = alog.list_all_gas_in_day('02-01-2020', 'h1')
#     gasexist1, index1 = alog.is_gas_exist_in_day('02-01-2020', 'O3', 'h1')
#     gasexist2, index2 = alog.is_gas_exist_in_day('01-01-2020', 'NO2', 'h1')
#     filename_list = alog.list_all_fileName_in_gasInfo(
#         '02-01-2020', 'NO2', 'h1')

#     gasinfo_exist, index = alog.is_gasInfo_exist_for_fileName(
#         '02-01-2020', 'NO2', 'name1', 'h1')
