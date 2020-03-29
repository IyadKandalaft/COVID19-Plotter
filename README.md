# COVID19-Plotter
A simple, interactive visualization tool for COVID-19 data built on top of the Plotly Dash framework.  The interface permits selecting data for each country to be plotted on the same figure to permit comparison between countries.  

Data source:
* Johns Hopkins CSSE - https://github.com/CSSEGISandData/COVID-19

## Starting the App

Clone this repository
    git clone https://github.com/IyadKandalaft/COVID19-plotter covid-plotter


Create a conda environment and install required modules
    conda create -n covid-plotter
    conda activate covid-plotter
    conda install -c plotly dash gunicorn urllib3

Change to the new directory
    cd covid-plotter

Start the app server
    ./run.py

Open your browser and navigate to http://localhost:8080

## Server Options

    -l LISTEN, --listen LISTEN
                          Interface address to listen on
    -p PORT, --port PORT  Port to listen on
    -w WORKERS, --workers WORKERS
                          Number of servers to start
    -t TEMPDIR, --tempdir TEMPDIR
                          Temporary data storage path
