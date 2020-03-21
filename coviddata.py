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
        self.data[country][COVIDEnum.INFECTED][date] = 0
        self.data[country][COVIDEnum.RECOVERED][date] = 0
        self.data[country][COVIDEnum.DEAD][date] = 0

    def _add_data_bydate(self, data_type: COVIDEnum, country: str, date: str, value: int):
        if country not in self.data:
            self._add_country(country)

        if date not in self.data[country][data_type]:
            self._add_date(country, date)

        # Add data from new record to existing value for that date
        # Existing value could be from records separted by province
        self.data[country][data_type][date] += value

        # Set the total to the latest record we have for that counrty
        latest_date = sorted(list(self.data[country][data_type])).pop()
        self.data[country]['total'][data_type] = self.data[country][data_type][latest_date]

    def get_total_infected(self, country: str):
        return self.get_total(COVIDEnum.INFECTED, country)

    def get_total_dead(self, country: str):
        return self.get_total(COVIDEnum.DEAD, country)

    def get_total_recovered(self, country: str):
        return self.get_total(COVIDEnum.RECOVERED, country)

    def get_total(self, data_type: COVIDEnum, country: str):
        return self.data[country]['total'][data_type]

    def get_infected_bydate(self, country: str, date: date, cumulative: bool = True):
        return self.get_bydate(COVIDEnum.INFECTED, country, date, cumulative)

    def get_dead_bydate(self, country: str, date: date, cumulative: bool = True):
        return self.get_bydate(COVIDEnum.DEAD, country, date, cumulative)

    def get_recovered_bydate(self, country: str, date: date, cumulative: bool = True):
        return self.get_bydate(COVIDEnum.RECOVERED, country, date, cumulative)

    def get_bydate(self, data_type: COVIDEnum, country: str, date: date, cumulative: bool = True):
        str_date = COVIDData._format_date(date)
        if str_date not in self.data[country][data_type]:
            return None

        if cumulative:
            return self.data[country][data_type][str_date]

        dates = sorted(list(self.data[country][data_type].keys()))
        # Subtractive data is calculated by subtracting from the target date's
        # cumulative value the previous date's cumulative value
        prev_day = dates(dates.index(date) - 1)
        return self.data[country][data_type][str_date] - self.data[country][data_type][prev_day]

    def get_infected_bycountry(self, country, cumulative: bool = True):
        return self.get_bycountry(COVIDEnum.INFECTED, country, cumulative)

    def get_dead_bycountry(self, country, cumulative: bool = True):
        return self.get_bycountry(COVIDEnum.DEAD, country, cumulative)

    def get_recovered_bycountry(self, country, cumulative: bool = True):
        return self.get_bycountry(COVIDEnum.RECOVERED, country, cumulative)

    def get_bycountry(self, data_type: COVIDEnum, country: str, cumulative: bool = True):
        if country not in self.data:
            return None

        if cumulative:
            return self.data[country][data_type]

        # Sort the keys (dates) because we can't rely on their order
        dates = sorted(list(self.data[country][data_type].keys()))
        # Subtractive data must be calculated from the existing cumulative data
        sub_data = self.data[country][data_type].copy()
        prev_day_total = 0
        for day in dates:
            prev_value = sub_data[day]
            sub_data[day] -= prev_day_total
            prev_day_total = prev_value

        return sub_data

    @staticmethod
    def _format_date(date: date):
        return str(date.year) + '-' + str(date.month).zfill(2) + '-' + str(date.day).zfill(2)
