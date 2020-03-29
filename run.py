#!/usr/bin/env python3

import argparse
from logging.config import dictConfig
import logging

import app
import coviddata
from dataloader import DataDownload
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

    logger.info("Preparing for data retrieval")
    data_download = DataDownload(opts.tempdir)
    data_download.add_download(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv",
        "covid19_confirmed.csv")
    data_download.add_download(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv",
        "covid19_deaths.csv")
    data_download.add_download(
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv",
        "covid19_recovered.csv")
    data_download.add_download(
        "https://population.un.org/wpp/Download/Files/1_Indicators%20(Standard)/CSV_FILES/WPP2019_TotalPopulationBySex.csv",
        "total_population_data.csv"
    )

    data_file_paths = data_download.download_all()

    data = {}
    for file_path in data_file_paths:
        if file_path.endswith('covid19_confirmed.csv'):
            data['infected'] = file_path
        elif file_path.endswith('covid19_deaths.csv'):
            data['dead'] = file_path
        elif file_path.endswith('covid19_recovered.csv'):
            data['recovered'] = file_path
        elif file_path.endswith('total_population_data.csv'):
            data['population'] = file_path

    logger.info('Parsing COVID-19 data')
    data_parser = coviddata.COVIDDataParser(
        data['infected'], data['recovered'], data['dead'])
    covid_data = data_parser.parse()

    logger.info('Parsing population data')
    population_data = populationdata.PopulationDataParser(
        data['population']).parse()
    population_data.add_country_aliases(
        'United States of America', 'US', 'USA')
    population_data.add_country_aliases(
        'Dem. People\'s Republic of Korea', 'North Korea', 'Korea, North')
    population_data.add_country_aliases(
        'Republic of Korea', 'South Korea', 'Korea, South')

    app.set_data(covid_data, population_data)
    app.create()

    server = app.start()

    options = {
        'bind': '%s:%s' % (opts.listen, opts.port),
        'workers': opts.workers
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
        prog='run.py',
        description="Graphs COVID-19 data"
    )

    parser.add_argument(
        "-l", "--listen",
        default="127.0.0.1",
        help="Interface address to listen on"
    )

    parser.add_argument(
        "-p", "--port",
        default=8080,
        help="Port to listen on"
    )

    parser.add_argument(
        "-w", "--workers",
        default=2,
        help="Number of servers to start"
    )

    parser.add_argument(
        "-t", "--tempdir",
        default='/tmp/covid19',
        help="Temporary data storage path"
    )

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
