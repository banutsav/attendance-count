from datetime import datetime
import calendar
from yattag import Doc
from pathlib import Path
import os
import html
import pandas as pd
from babel.numbers import format_currency
import plotly.graph_objects as go
import plotly.offline as opy

# Save plot to file
def writeResults(figures):
	doc, tag, text = Doc().tagtext()
	# Generate HTML
	with tag('html'):
		with tag('head'):
			with tag('script', src="https://cdn.plot.ly/plotly-latest.min.js"):
				pass
			with tag('title'):
				text('Attendance Results')
		with tag('body'):
			for figure in figures:	
				with tag('div'):
					text(figure)
				
	result = doc.getvalue()
	outfile = Path(Path(os.getcwd()) / 'output/results.html')
	f = open(outfile, "w")
	f.write(html.unescape(result))
	f.close() 

# Stacked bar with different attendance categories
def stackedAttCat(direct, indirect, cats):
	# Get total indirect and diect emloyees
	totdirect = 0; totindirect = 0
	for i in range(len(cats)):
		totdirect += direct[i]
		totindirect += indirect[i]
	# Create hovertexts
	dhover = []; ihover = []
	for i in range(len(cats)):
		dhover.append(str(direct[i]) + ' (' + str(round((direct[i]/totdirect)*100)) + '%) direct employees' 
			+ '<br>have an attendance ' + str(cats[i]) + ' days')
		ihover.append(str(indirect[i]) + ' (' + str(round((indirect[i]/totindirect)*100)) + '%) indirect employees'
			+ '<br>have an attendance of ' + str(cats[i]) + ' days')
	# Create stacked bar
	fig = go.Figure(data=[
    	go.Bar(name='Direct', x=cats, y=direct, marker_color='lightgreen', hovertext=dhover, hoverinfo='text'),
    	go.Bar(name='In-Direct', x=cats, y=indirect, marker_color='lightsalmon', hovertext=ihover, hoverinfo='text')
	])

	# Change the bar mode
	fig.update_layout(title='Employee Attendances', barmode='stack')
	fig.update_yaxes(showticklabels=False)
	plot = opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False, config={'displayModeBar':False})
	return plot

# Separate attendances into categories - >25, 20-25, <25
def catAttendance(file):
	print('Categorizing attendance counts from',file)
	# Construct a dataframe for employee salaries
	df = pd.read_csv(file)
	# making new data frame with dropped NA values 
	df = df.dropna(axis = 0, how ='any')
	df.set_index('EmpNo', inplace=True)
	# Initialize arrays for attendance categories
	direct = [0,0,0] # Direct Employees
	indirect = [0,0,0] #Indirect Employees
	cats = ['Above 25', '20-25', 'Below 20']
	# Iterate across employees
	for index, row in df.iterrows():
		count = row['Salary']
		cat = row['EmpType']
		# Direct employees
		if (cat == 'direct'):
			if ( count >= 25):
				direct[0] += 1
			elif (count >= 20):
				direct[1] += 1
			else:
				direct[2] += 1
		# Indirect employees
		else:
			if ( count >= 25):
				indirect[0] += 1
			elif (count >= 20):
				indirect[1] += 1
			else:
				indirect[2] += 1
	
	plot = stackedAttCat(direct, indirect, cats)
	return plot

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
	fig.update_layout(title='Daily Cost for direct employees')
	plot = opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False, config={'displayModeBar':False})
	return plot

# Master module for creating visualizations and reports
def vizMaster(attfile, costfile):
	print('Constructing visualizations...')
	# Create visualizations
	figures = []
	figures.append(catAttendance(attfile))
	figures.append(scatterPerDayCost(costfile))
	writeResults(figures)
	print('Creation of visualizations completed...')