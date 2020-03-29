import dash_core_components as dcc
import dash_html_components as html
import logging

from coviddata import COVIDData
from populationdata import PopulationData

logger = logging.getLogger(__name__)

covid_data = []
population_data = None


def create_layout(app):
    """Create the Dash application components and configure them into a layout

    Arguments:
        app {Dash} -- Dash application that will receive the layout
    """
    logger.info('Creating application components')

    logger.debug('Creating top level DIV')
    page = html.Div(children=[])

    logger.debug('Creating application title')
    page_title = html.H1(
        id='app-title', children='COVID-19 Global Data Plotter'
    )

    logger.debug('Creating appliaction description DIV')
    app_description = html.Div(
        children='''This COVID-19 data visualization tool allow you to simply
        browse available global data on those that are infected, recovered,
        or have died.'''
    )

    logger.debug('Creating search Dropdown')
    search_field = dcc.Dropdown(
        id='search-field', multi=True, clearable=True, options=[],
        searchable=True, placeholder='Select country data to plot'
    )
    _populate_search(search_field)

    logger.debug('Creating main-plot Graph')
    main_plot = dcc.Graph(
        id='main-plot',
        figure={
            'data': [],
            'layout': {
                'title': 'Dash Data Visualization'
            }
        },
        config={
            'editable': True,
            'showTips': True
        }
    )

    logger.debug('Creating normalization radio buttons')
    normalization_rb = dcc.RadioItems(
        id='normalization-rb',
        labelStyle={
            'display': 'block'
        },
        options=[
            {'label': 'None', 'value': 'none'},
            {'label': 'Per 1000 people', 'value': 'per-1000'},
            {'label': 'Per capita', 'value': 'per-capita'}
        ],
        value='none',
    )
    normalization_fs = html.Fieldset(
        style={
            'display': 'inline-block'
        },
        children=[
            html.Legend(children='Normalization'),
            normalization_rb
        ],
        draggable=True,

    )

    logger.debug('Creating infected chart type radio buttons')
    chart_option_elems = []
    for data_type in ('infected', 'dead', 'recovered'):
        chart_type_rb = dcc.RadioItems(
            id=f'chart-{data_type}-rb',
            labelStyle={
                'display': 'block'
            },
            options=[
                {'label': 'Line', 'value': 'line'},
                {'label': 'Bar', 'value': 'bar'},
            ],
            value='line',
        )
        chart_option_elems.append(
            html.Fieldset(
                style={
                    'display': 'inline-block'
                },
                children=[
                    html.Legend(children=f'Plot Type ({data_type})'),
                    chart_type_rb
                ],
                draggable=True
            )
        )
    logger.debug('Adding sub-components to top-level DIV')
    page.children.append(page_title)
    page.children.append(app_description)
    page.children.append(search_field)
    page.children.append(normalization_fs)
    page.children.extend(chart_option_elems)
    page.children.append(main_plot)

    logger.info('Setting application layout')
    app.layout = page


def _populate_search(dropdown: dcc.Dropdown):
    """Populate the search Dropdown component with the names of datasets that
    are plottable 

    Arguments:
        dropdown {dcc.Dropdown} -- Dropdown object that will be populated
    """
    countries = covid_data.get_countries()
    logger.info(f'Populating countries in search dropdown ({len(countries)})')
    for country in countries:
        logger.debug(f'Processing country {country}')
        dropdown.options.append(
            {'label': f'{country} (Infected)', 'value': f'{country}:infected'})
        dropdown.options.append(
            {'label': f'{country} (Dead)', 'value': f'{country}:dead'})
        dropdown.options.append(
            {'label': f'{country} (Recovered)', 'value': f'{country}:recovered'})

    dropdown.value = ['Canada:infected', 'Canada:recovered', 'Canada:dead']


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
