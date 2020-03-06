<small>created by [wesley beckner](http://wesleybeckner.github.io)</small>

# Energy Dashboard

This is an [energy dashboard](https://belpre.herokuapp.com) demo using [Dash](https://plot.ly/products/dash/) 

## Getting Started

### Running the app locally

First create a virtual environment with conda (or venv) and activate it.

```

conda create -n <your_env_name> python==3.7
source activate <your_env_name>

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/wesleybeckner/energy.git
cd energy
pip install -r requirements.txt

```

Run the app

```

python app.py

```

## About the app

This is an interactive app for high-level viewing of manufacturing energy consumption data with green house gas emission

1. Corporate management level
    * Output KPIs:
        * Energy intensity – unit GJ/mt of production 
        * GHG intensity – unit mtCO2/ton of production
        * Reporting frequency: quarterly – display monthly actuals and cumulative year
        * Reporting/Visualizing method: Dash/Flask + python

2. Plant management level
    * Output KPIs:
        * Plant energy intensity – unit GJ/mt of production
        * Plant GHG intensity – unit GJ/mt of production
        * Plant energy consumption total – GJ + local unit
        * Plant GHG total – mtCO2
        * Reporting frequency: monthly, cumulative year
        * Reporting/Visualizing method: Dash/Flask + python


## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
