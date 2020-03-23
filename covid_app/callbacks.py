from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import logging

from coviddata import COVIDData
from populationdata import PopulationData

logger = logging.getLogger(__name__)

covid_data = None
population_data = None


def register_callbacks(app):
    """Configure the callbacks that are executed when the user interacts with
    components in the application

    Arguments:
        app {Dash} -- Dash application that will receive the callbacks
    """
    logger.info('Registering Dash callbacks')

    @app.callback(
        Output('main-plot', 'figure'),
        [
            Input('search-field', 'value'),
            Input('normalization-rb', 'value')
        ]
    )
    def search_callback(request_items, normalization):
        """Callback that generates the data for the main-plot figure

        Arguments:
            request_items {list} -- Values of the search dropdown
            normalization {str} -- Value of the normalization radio button group

        Returns:
            dict -- Data structure that updates the main-plot figure parameter
        """
        if request_items is None:
            return _get_plot_dict()

        logger.info('Search callback was trigger')
        plot_data = []
        for request_item in request_items:
            logger.debug(f'Processing request item {request_item}')

            (country, data_type) = request_item.split(':')
            if data_type == 'recovered':
                country_data = covid_data.get_recovered_bycountry(country)
            elif data_type == 'dead':
                country_data = covid_data.get_dead_bycountry(country)
            else:
                country_data = covid_data.get_infected_bycountry(country)

            country_pop = population_data.get_total(country)

            x = list(country_data.keys())
            if normalization == 'per-1000':
                y = list(v * 1000 / country_pop for v in country_data.values())
            elif normalization == 'per-capita':
                y = list(v / country_pop for v in country_data.values())
            else:
                y = list(country_data.values())

            plot_data.append(
                {
                    'type': 'line',
                    'x': x,
                    'y': y,
                    'text': f'{country} ({data_type})',
                    'name': f'{country} ({data_type})'
                }
            )
        return _get_plot_dict(plot_data)


def _get_plot_dict(data_points: list = []):
    return {
        'data': data_points,
        'layout': {
            'title': 'COVID-19 Data'
        }
    }


def _set_data(input_covid_data: COVIDData, input_pop_data: PopulationData):
    """Pass data into the application to permit access to Dash components

    Arguments:
        input_covid_data {COVIDData} -- COVID-19 datasets
        input_pop_data {PopulationData} -- Population datasets
    """
    global covid_data
    global population_data

    covid_data = input_covid_data
    population_data = input_pop_data
