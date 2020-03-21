#!/usr/bin/env python3

import coviddata
import argparse
from logging.config import dictConfig
import logging
import plotly.graph_objects as go

# Setup logging
logging_config = dict(
    version = 1,
    formatters = {
        'f': {'format':
              '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'}
        },
    handlers = {
        'h': {'class': 'logging.StreamHandler',
              'formatter': 'f',
              'level': logging.DEBUG}
        },
    root = {
        'handlers': ['h'],
        'level': logging.DEBUG,
        },
)
dictConfig(logging_config)
logger = logging.getLogger()


def main():
    opts = get_config()
    data_parser = coviddata.COVIDDataParser(opts.infected, opts.recovered, opts.dead)
    covid_data = data_parser.parse()
    print(covid_data.get_infected_bycountry('Canada'))
    

def get_config():
    '''
    Defines the command line parameters and returns the parameters passed to the script

    Returns:
        argparse.args -- An object containing the parsed command line parameters
    '''
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
    
    return parser.parse_args()

if __name__ == "__main__":
    main()