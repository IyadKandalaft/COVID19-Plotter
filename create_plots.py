#!/usr/bin/env python3

import argparse
from logging.config import dictConfig
import logging

import app
import coviddata


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
    data_parser = coviddata.COVIDDataParser(
        opts.infected, opts.recovered, opts.dead)
    covid_data = data_parser.parse()

    app.set_data(covid_data)
    app.create()

    server = app.start()


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

    logger.debug('Parsing and validating command line parameters')
    return parser.parse_args()


if __name__ == "__main__":
    main()
