from datetime import datetime
import calendar
from yattag import Doc
from pathlib import Path
import os
import pandas as pd
from babel.numbers import format_currency
import plotly.graph_objects as go
import plotly.offline as opy

# Get day from date
def dayFromDate(date):
	tokens = date.split('-')
	today = datetime.today()
	fulldate = tokens[0] + '-' + tokens[1] + '-' + str(today.year)
	day = datetime.strptime(fulldate, '%d-%b-%Y').weekday()
	text = '<b>' + str(fulldate) + '</b><br>' + str(calendar.day_name[day]) + '<br>'
	return text
	
# Per day cost variation
def scatterPerDayCost(file):
	print('Visualising per day cost variation from', file)
	df = pd.read_csv(file)
	# making new data frame with dropped NA values 
	df = df.dropna(axis = 0, how ='any')
	# Create hover text
	hovertext = [];
	for index, row in df.iterrows():
		hovertext.append(dayFromDate(row['Day']) + str(format_currency(row['Cost'],'INR',locale='en_IN')))
	# Create Scatte Plot
	fig = go.Figure()
	fig.add_trace(go.Scatter(x=df['Day'], y=df['Cost'], mode='lines+markers',
		hovertext=hovertext, hoverinfo='text', 
		marker=dict(size=15, color='lightgreen'),
		))
	fig.update_xaxes(showticklabels=False)
	fig.update_yaxes(showticklabels=False)
	plot = opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False, config={'displayModeBar':False})
	return plot