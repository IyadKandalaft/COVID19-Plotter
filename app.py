import covid_app.callbacks
import covid_app.layout
import logging

import dash
from coviddata import COVIDData
from populationdata import PopulationData

logger = logging.getLogger(__name__)

# Application handle
app = None
covid_data = None
population_data = None


def create():
    """Create the Dash application and register the layout and callbacks

    Returns:
        Dash -- A Dash application object
    """
    global app

    logger.info('Creating Dash application')
    app = dash.Dash('COVID-19')
    covid_app.layout.create_layout(app)
    covid_app.callbacks.register_callbacks(app)

    return app


def set_data(input_covid_data: COVIDData, input_pop_data: PopulationData):
    """Pass data into the application to permit access to Dash components

    Arguments:
        input_covid_data {COVIDData} -- COVID-19 datasets
        input_pop_data {PopulationData} -- Population datasets
    """
    global covid_data
    global population_data

    covid_data = covid_data
    population_data = input_pop_data
    
    covid_app.callbacks._set_data(input_covid_data, input_pop_data)
    covid_app.layout._set_data(input_covid_data, input_pop_data)


def start():
    """Start the Dash application

    Returns:
        Server -- A flask server object
    """
    global app

    if app != None:
        logger.debug('Starting flask server')
        
        return app.server
    
    return None
