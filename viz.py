import os
import time
import math
import html
import pandas as pd
from yattag import Doc
import plotly.graph_objects as go
import plotly.offline as opy
from pathlib import Path
from datetime import datetime

# Custom imports
import hr
import production

# Save plot to file
def writeResults(figures, filename):
	doc, tag, text = Doc().tagtext()
	# Generate HTML
	with tag('html'):
		with tag('head'):
			with tag('script', src="https://cdn.plot.ly/plotly-latest.min.js"):
				pass
			with tag('title'):
				text('svg-reports')
		with tag('body'):
			for figure in figures:	
				with tag('div', id=figure):
					text(figures[figure])
				
	result = doc.getvalue()
	outfile = Path(Path(os.getcwd()) / 'output/' / filename)
	f = open(outfile, "w")
	f.write(html.unescape(result))
	f.close()

if __name__ == '__main__':
	start = time.time()
	print('Execution started...')

	# Setup files and input directories
	datasource = Path(Path(os.getcwd()) / 'input')
	attfile = Path(Path(os.getcwd()) / 'output/attendance-count.csv')
	cost_for_day_file = Path(Path(os.getcwd()) / 'output/cost-per-day.csv')
	
	# HR
	
	emptimes, dates = hr.getEmpTimes(datasource)
	direct, indirect, cats = hr.catAttendance(attfile)

	figures = {
		#'times': hr.stackedTimes(emptimes),
		#'attcats': hr.stackedAttCat(direct, indirect, cats),
		'latecomers': hr.stackedLates(attfile, dates),
	}
	writeResults(figures,'hr.html')

	# Production
	figures = {
		'dempcost': production.scatterPerDayCost(cost_for_day_file)
	}
	writeResults(figures, 'prod.html')
	
	end = time.time()
	print('Execution finished in',str(round(end-start,2)),'secs')
