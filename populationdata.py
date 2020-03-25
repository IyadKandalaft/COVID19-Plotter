import logging
from enum import Enum
from datetime import date
import csv
from typing import NamedTuple

logger = logging.getLogger(__name__)


class PopulationEnum(Enum):
    DENSITY = 'density'
    TOTAL = 'total'
    MALE = 'male'
    FEMALE = 'female'


class PopulationDataParser(object):
    """A convenience class that parses a population csv file

    """

    def __init__(self, pop_csv: str, skip_first: int = 1):
        """Initialize a PopulationDataParser object

        Arguments:
            pop_csv {str} -- Path to a csv file containing population data

        Keyword Arguments:
            skip_first {int} -- Skip the first n lines in the csv file (default: {1})
        """
        super().__init__()
        self.skip_first = skip_first
        self.data_file = pop_csv

    def parse(self):
        """Parse the csv file and return the population data as an object

        Returns:
            PopulationData -- Population data encapsulation object
        """
        pop_data = PopulationData()
        with open(self.data_file, buffering=131072) as f:
            logger.info(f'Parsing population data file {self.data_file}')

            csv_reader = csv.reader(f, delimiter=',', quotechar='"')
            line_count = 0
            for line in csv_reader:
                line_count += 1
                if line_count <= self.skip_first:
                    continue
                try:
                    (locid, country, varid, variant, year, midperiod, str_pop_male,
                     str_pop_female, str_pop_total, str_pop_density) = line
                except ValueError as e:
                    logger.debug(
                        f'Incorrect number of columns in {data_file.path}:{line_count}\n' +
                        f'Line content: {line}'
                    )
                    continue

                year = int(year)
                country = country.lower()

                if str_pop_male == '':
                    str_pop_male = 0
                if str_pop_female == '':
                    str_pop_female = 0
                if str_pop_total == '':
                    str_pop_total = 0
                if str_pop_density == '':
                    str_pop_density = 0

                pop_male = int(float(str_pop_male) * 1000)
                pop_female = int(float(str_pop_female) * 1000)
                pop_total = int(float(str_pop_total) * 1000)
                pop_density = int(float(str_pop_density) * 1000)

                pop_data.add_data(PopulationEnum.MALE,
                                  country, year, pop_male)
                pop_data.add_data(PopulationEnum.FEMALE,
                                  country, year, pop_female)
                pop_data.add_data(PopulationEnum.TOTAL,
                                  country, year, pop_total)
                pop_data.add_data(PopulationEnum.DENSITY,
                                  country, year, pop_density)

            logger.debug(
                f'Parsed {line_count - self.skip_first} population data points')
        return pop_data


class PopulationData(dict):
    """Population data encapsulation class to facilitate retrieving the data 
    using convenienec methods.
    """

    def __init__(self):
        super().__init__()
        self.data = {}

    def add_data(self, data_type: PopulationEnum, country: str, year: int, val: int):
        """Add a population data point

        Arguments:
            data_type {PopulationEnum} -- The type of data being provided
            country {str} -- The country name
            year {int} -- The year of the data point
            val {int} -- The population value for that year
        """
        if country == '':
            raise ValueError('Country cannot be empty')

        if year < 1:
            raise ValueError('Year must be a positive integer')

        self._add_data(data_type, country, year, val)

    def _add_country(self, country: str):
        """Create the an empty data structure for a country

        Arguments:
            country {str} -- The country name
        """
        self.data[country] = {
            'aliases': [],
            PopulationEnum.MALE: {},
            PopulationEnum.FEMALE: {},
            PopulationEnum.TOTAL: {},
            PopulationEnum.DENSITY: {},
        }

    def add_country_aliases(self, country: str, *aliases: str):
        """Add aliases to a country that will be used for country lookups

        Arguments:
            country {str} -- The country name
            *aliases {str} -- The aliases to added
        """
        country = country.lower()
        if country not in self.data:
            raise ValueError('Failed to add aliases for {country} because it does not exist in the data')
        for alias in list(aliases):
            self.data[country]['aliases'].append(alias.lower())

    def _add_year(self, country: str, year: int):
        for pop_type in PopulationEnum:
            self.data[country][pop_type][date] = 0

    def _add_data(self, data_type: PopulationEnum, country: str, year: int, val: int):
        if country not in self.data:
            self._add_country(country)

        if year not in self.data[country][data_type]:
            self._add_year(country, year)

        self.data[country][data_type][year] = val

    def get_countries(self):
        """Get a list of countries that have data

        Returns:
            list -- List of countries
        """
        return list(self.data.keys())

    def get_total(self, country: str, year=None):
        """Get the total population for the requested country

        Arguments:
            country {str} -- The country name

        Keyword Arguments:
            year {[type]} -- The year of interest. Keep as None to use the 
                             current year (default: {None})

        Returns:
            int -- Population total
        """
        return self._get_data(PopulationEnum.TOTAL, country, year)

    def get_density(self, country: str, year=None):
        """Get the population density for the requested country

        Arguments:
            country {str} -- The country name

        Keyword Arguments:
            year {[type]} -- The year of interest. Keep as None to use the 
                             current year (default: {None})

        Returns:
            int -- Population density
        """
        return self._get_data(PopulationEnum.DENSITY, country, year)

    def get_female(self, country: str, year=None):
        """Get the female population for the requested country

        Arguments:
            country {str} -- The country name

        Keyword Arguments:
            year {[type]} -- The year of interest. Keep as None to use the 
                             current year (default: {None})

        Returns:
            int -- Female population
        """
        return self._get_data(PopulationEnum.FEMALE, country, year)

    def get_male(self, country: str, year=None):
        """Get the male population for the requested country

        Arguments:
            country {str} -- The country name

        Keyword Arguments:
            year {[type]} -- The year of interest. Keep as None to use the 
                             current year (default: {None})

        Returns:
            int -- Male population
        """
        return self._get_data(PopulationEnum.MALE, country, year)

    def _get_data(self, data_type: PopulationEnum, country: str, year=None):
        country = country.lower()
        if year is None:
            year = date.today().year

        if country not in self.data:
            country = self._search_country_alias(country)
            if country is None:
                return -1

        if year not in self.data[country][data_type]:
            return -1

        return self.data[country][data_type][year]

    def _search_country_alias(self, country):
        for key in self.data.keys():
            if country in self.data[key]['aliases']:
                return key
        return None
