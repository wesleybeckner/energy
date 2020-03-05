<small>[wesley beckner](http://wesleybeckner.github.io)</small>

# Energy Dashboard

This is an energy dashboard demo using [Dash](https://plot.ly/products/dash/) 

## Getting Started

### Running the app locally

First create a virtual environment with conda or venv inside a temp folder, then activate it.

```
virtualenv venv

# Windows
venv\Scripts\activate
# Or Linux
source venv/bin/activate

```

Clone the git repo, then install the requirements with pip

```

git clone https://github.com/plotly/dash-sample-apps
cd dash-sample-apps/apps/dash-financial-report
pip install -r requirements.txt

```

Run the app

```

python app.py

```

## About the app

This is an interactive app for high-level viewing of manufacturing energy consumption data with green house gas emission

o	Corporate Management level – Ops lead team, Sustainability council
	Output KPI’s:
•	Energy intensity Kraton – unit GJ/mt of production 
•	GHG intensity Kraton – unit mtCO2/ton of production
•	Reporting frequency: quarterly – display monthly actuals and cumulative year
•	Split between Polymer segment and Chemical segment
•	Reporting/Visualizing method: new system
•	
o	Plant management level – Plant lead team (+ info screens)
•	Plant energy intensity – unit GJ/mt of production
•	Plant GHG intensity – unit GJ/mt of production
•	Plant energy consumption total – GJ + local unit
•	Plant GHG total – mtCO2
•	Reporting frequency: monthly, cumulative year
•	Reporting/Visualizing method: new system


## Built With

- [Dash](https://dash.plot.ly/) - Main server and interactive components
- [Plotly Python](https://plot.ly/python/) - Used to create the interactive plots
