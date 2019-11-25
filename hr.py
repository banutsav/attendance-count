import os
import re
from pathlib import Path
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.offline as opy
import production as prod

# CONSTANTS
LOT_OF_TEXT = 25

# Create a short text for the hover info
def shortenText(words):
	l = len(words)
	# Less than 5 strings, concatenate and return
	if l <= LOT_OF_TEXT:
		return ('<br>' + '<br>'.join(words))
	
	text = ''
	# More than 5 strings
	for i in range(LOT_OF_TEXT):
		text = text + '<br>' + words[i]
	text = text + '<br>' + '...and ' + str(l - LOT_OF_TEXT) + ' more'
	return text

# Latecomers per day categorized into direct and indirect
def stackedLates(attfile, dates):
	# Data for plotting
	dcount = []; icount = []; dhover = []; ihover = []
	print('Late attendances from',attfile)
	# Construct a dataframe for employee salaries
	df = pd.read_csv(attfile)
	# making new data frame with dropped NA values 
	df = df.dropna(axis = 0, how ='any')
	df.set_index('EmpNo', inplace=True)
	# Iterate over the range of dates
	for date in dates:
		dc = 0; ic = 0; dnames = []; inames = []
		# Calculate number of direct and indirect latecomers
		for index, row in df.iterrows():
			if ('L' in row[date]):
				# Get the intime
				tokens = row[date].split(' '); intime = tokens[1]
				if(row['EmpType'] == 'direct'):
					dc += 1; dnames.append(str(index) + ' ' + row['Name'] + ' ' + intime)
				elif(row['EmpType'] == 'indirect'):
					ic += 1; inames.append(str(index) + ' ' + row['Name'] + ' ' + intime)
		
		dcount.append(dc); icount.append(ic)
		dhover.append('<b>' + date + ', ' + str(dc) + ' direct employees</b>' + shortenText(dnames))
		ihover.append('<b>' + date + ', ' + str(ic) + ' indirect employees</b>' + shortenText(inames))

	# Create stacked bar graph
	fig = go.Figure(data=[
    	go.Bar(name='Direct', x=dates, y=dcount, marker_color='lightsalmon', hovertext=dhover, hoverinfo='text'),
    	go.Bar(name='In-Direct', x=dates, y=icount, marker_color='lightgreen', hovertext=ihover, hoverinfo='text')
	])

	# Change the bar mode
	fig.update_layout(barmode='stack')
	fig.update_xaxes(showticklabels=False)
	fig.update_yaxes(showticklabels=False)
	plot = opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False, config={'displayModeBar':False})
	return plot

def computeTimes(df):
	timecats = {'6-8':[], '8-9': [], '9-10': [], '10-11': [], 'after-11': []}

	for index, row in df.iterrows():
		status = row['Status']
		emp = row['Name']
		if ('Present' in  status):
			if(pd.isna(row['InTime'])):
				continue
			intime = (datetime.strptime(row['InTime'], '%H:%M')).hour
			if ( intime == 6 or intime == 7 ):
				timecats['6-8'].append(emp)
			elif ( intime == 8 ):
				timecats['8-9'].append(emp)
			elif ( intime == 9 ):
				timecats['9-10'].append(emp)
			elif ( intime == 10 ):
				timecats['10-11'].append(emp)
			elif ( intime >= 11 and intime < 16):
				timecats['after-11'].append(emp)

	return timecats

def getEmpTimes(datasource):
	emptimes = {}
	dates = []
	for filename in os.listdir(datasource):
		if filename.endswith('.csv') and not 'salary' in filename:
			# Get date from filename
			date = os.path.splitext(filename)[0]
			# Get source file path
			filepath = Path(Path(datasource) / filename)
			# Create Data Frame
			df = pd.read_csv(filepath, index_col='E. Code')
			#print(filename)
			emptimes[date] = computeTimes(df)
			dates.append(date)
	
	# Sort dates
	dates.sort(key = lambda date: datetime.strptime(date, '%d-%b'))

	return emptimes, dates

def createStackHover(dates, emptimes, cat):
	hover = []
	for date in dates:
		text = prod.dayFromDate(date) + str(len(emptimes[date][cat])) + ' Employees<br>'
		for x in emptimes[date][cat]:
			text = text + x + '<br>'
		hover.append(text)
	return hover

def stackedTimes(emptimes):
	dates = list(emptimes.keys())
	# Sort dates
	dates.sort(key = lambda date: datetime.strptime(date, '%d-%b'))
	# Create stacked bar
	fig = go.Figure(data=[
    	go.Bar(name='8am-9am', x=dates, y=[len(emptimes[x]['8-9']) for x in dates], marker_color='lightgray'
    		, hovertext=createStackHover(dates, emptimes, '8-9'), hoverinfo='text'),
    	go.Bar(name='9am-10am', x=dates, y=[len(emptimes[x]['9-10']) for x in dates], marker_color='lightgreen'
    		, hovertext=createStackHover(dates, emptimes, '9-10'), hoverinfo='text'),
    	go.Bar(name='10am-11am', x=dates, y=[len(emptimes[x]['10-11']) for x in dates], marker_color='lightblue'
    		, hovertext=createStackHover(dates, emptimes, '10-11'), hoverinfo='text'),
    	go.Bar(name='After 11am', x=dates, y=[len(emptimes[x]['after-11']) for x in dates], marker_color='lightsalmon'
    		, hovertext=createStackHover(dates, emptimes, 'after-11'), hoverinfo='text')
	])
	# Change the bar mode
	fig.update_layout(barmode='stack', legend_orientation="h")
	fig.update_yaxes(showticklabels=False)
	fig.update_xaxes(showticklabels=False)
	plot = opy.plot(fig, auto_open=False, output_type='div', include_plotlyjs=False, config={'displayModeBar':False})
	return plot

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
	fig.update_layout(barmode='stack')
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
		count = row['Count']
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
	
	return direct, indirect, cats
