#!/usr/bin/env python3

import argparse
from logging.config import dictConfig
import logging

import app
import coviddata
import gunicorn.app.base
import populationdata


# Setup logging
logging_config = dict(
    version=1,
    formatters={
        'default': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'
        }
    },
    handlers={
        'handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    root={
        'handlers': ['handler'],
        'level': 'DEBUG',
    },
)
dictConfig(logging_config)
logger = logging.getLogger(__name__)


def main():
    opts = get_config()

    logger.info('Parsing COVID-19 data')
    data_parser = coviddata.COVIDDataParser(
        opts.infected, opts.recovered, opts.dead)
    covid_data = data_parser.parse()

    logger.info('Parsing population data')
    population_data = populationdata.PopulationDataParser(
        opts.population).parse()
    population_data.add_country_aliases('United States of America', 'US', 'USA')
    population_data.add_country_aliases('Dem. People\'s Republic of Korea', 'North Korea', 'Korea, North')
    population_data.add_country_aliases('Republic of Korea', 'South Korea', 'Korea, South')

    app.set_data(covid_data, population_data)
    app.create()

    server = app.start()
    
    options = {
        'bind': '%s:%s' % ('0.0.0.0', '9000'),
        'workers': 2
    }
    StandaloneApplication(server, options).run()

def get_config():
    '''
    Defines the command line parameters and returns the parameters passed to the script

    Returns:
        argparse.args -- An object containing the parsed command line parameters
    '''
    logger.debug('Configuring command line parameters')

    parser = argparse.ArgumentParser(
        prog='create_graphs.py',
        description="Graphs COVID-19 data")

    parser.add_argument(
        "-i", "--infected",
        required=True,
        help="Infected data file")

    parser.add_argument(
        "-r", "--recovered",
        required=True,
        help="Recovered data file")

    parser.add_argument(
        "-d", "--dead",
        required=True,
        help="Dead data file")

    parser.add_argument(
        "-p", "--population",
        required=True,
        help="Population data file")

    logger.debug('Parsing and validating command line parameters')
    return parser.parse_args()

class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    main()
