import logging
from enum import Enum
from datetime import date
from typing import NamedTuple

logger = logging.getLogger('coviddata')


class COVIDEnum(Enum):
    INFECTED = 'infected'
    DEAD = 'dead'
    RECOVERED = 'recovered'


class DataFile(NamedTuple):
    data_type: COVIDEnum
    path: str


class COVIDDataParser(object):
    def __init__(self, infected_csv, dead_csv, recovered_csv, skip_first=2):
        super().__init__()
        self.data_files = []

        self.data_files.append(DataFile(COVIDEnum.INFECTED, infected_csv))
        self.data_files.append(DataFile(COVIDEnum.RECOVERED, recovered_csv))
        self.data_files.append(DataFile(COVIDEnum.DEAD, dead_csv))
        self.skip_first = skip_first

    def parse(self):
        covid_data = COVIDData()

        for data_file in self.data_files:
            with open(data_file.path) as f:
                line_count = 0
                for line in f:
                    line_count += 1
                    if line_count <= self.skip_first:
                        continue
                    try:
                        (province, country, geo_lat, geo_long,
                         str_date, str_value) = line.split(',')
                    except ValueError as e:
                        logger.debug(
                            f'Incorrect number of columns in {data_file.path}:{line_count}\n' +
                            f'Line content: {line}'
                        )
                        continue
                    date = COVIDDataParser._parse_date(str_date)
                    value = int(str_value)

                    covid_data.add_data(data_file.data_type,
                                        country, date, value)

        return covid_data

    @staticmethod
    def _parse_date(str_date: str):
        (year, month, day) = list(map(int, str_date.split('-')))
        return date(year, month, day)


class COVIDData(dict):
    """[summary]

    Arguments:
        object {[type]} -- [description]
    """

    def __init__(self):
        super().__init__()
        self.data = {}

    def add_data(self, data_type: COVIDEnum, country: str, date: date, val: int):
        if country == '':
            raise ValueError('Country cannot be empty')
        try:
            str_date = COVIDData._format_date(date)
        except AttributeError as e:
            raise ValueError('Date must be a valid date object')

        if not (val >= 0 and val < 999999):
            raise ValueError('Value must be an integer between 0 and 999999')

        self._add_data_bydate(data_type, country, str_date, val)

    def _add_country(self, country: str):
        self.data[country] = {
            COVIDEnum.INFECTED: {},
            COVIDEnum.RECOVERED: {},
            COVIDEnum.DEAD: {},
            'total': {
                COVIDEnum.INFECTED: 0,
                COVIDEnum.RECOVERED: 0,
                COVIDEnum.DEAD: 0
            }
        }

    def _add_date(self, country: str, date: str):
        self.data[country][COVIDEnum.INFECTED][date] = None
        self.data[country][COVIDEnum.RECOVERED][date] = None
        self.data[country][COVIDEnum.DEAD][date] = None

    def _add_data_bydate(self, data_type: COVIDEnum, country: str, date: str, value: int):
        if country not in self.data:
            self._add_country(country)
        self.data[country]['total'][data_type] += value

        if date not in self.data[country][data_type]:
            self._add_date(country, date)
        self.data[country][data_type][date] = value

    def get_total_infected(self, country: str):
        return self.get_total(COVIDEnum.INFECTED, country)

    def get_total_dead(self, country: str):
        return self.get_total(COVIDEnum.DEAD, country)

    def get_total_recovered(self, country: str):
        return self.get_total(COVIDEnum.RECOVERED, country)

    def get_total(self, data_type: COVIDEnum, country: str):
        return self.data[country]['total'][data_type]

    def get_infected_bydate(self, country: str, date: date):
        return self.get_bydate(COVIDEnum.INFECTED, country, date)

    def get_dead_bydate(self, country: str, date: date):
        return self.get_bydate(COVIDEnum.DEAD, country, date)

    def get_recovered_bydate(self, country: str, date: date):
        return self.get_bydate(COVIDEnum.RECOVERED, country, date)

    def get_bydate(self, data_type: COVIDEnum, country: str, date: date):
        str_date = COVIDData._format_date(date)
        if str_date in self.data[country][data_type]:
            return self.data[country][data_type][str_date]
        return None

    def get_infected_bycountry(self, country):
        return self.get_bycountry(COVIDEnum.INFECTED, country)

    def get_dead_bycountry(self, country):
        return self.get_bycountry(COVIDEnum.DEAD, country)

    def get_recovered_bycountry(self, country):
        return self.get_bycountry(COVIDEnum.RECOVERED, country)

    def get_bycountry(self, data_type:COVIDEnum, country: str):
        if country in self.data:
            return self.data[country][data_type]
        return None

    @staticmethod
    def _format_date(date: date):
        str_date_list = list(map(str, [date.year, date.month, date.day]))
        return '-'.join(str_date_list)
