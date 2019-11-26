from pathlib import Path
import os
import pandas as pd

# Constants
# Salary grade for labor
LOW_SALARY = 10000

# 'NS' == 'B SHIFT' i.e. night shift
# 'GS' == 'A SHIFT' i.e. day shift

def checkLate(emp, intime, shift, dfsalary):
	# Get the daily salary for a person	
	salary = dfsalary.loc[emp,'Total Salary'] if emp in dfsalary.index else 0
	tokens = intime.split(':')
	hour = int(tokens[0])
	mins = int(tokens[1])
	late = 'L (' + intime + ')' 
	# indirect employees
	if (salary < LOW_SALARY):
		
		# day shift
		if (shift == 'GS') or (shift == 'A SHIFT'):
			if hour > 7:
				return late
			#elif hour == 7 and mins > 30:
			#	return late
		
		# night shift
		elif (shift == 'NS') or (shift == 'B SHIFT'):
			if hour > 19:
				return late
			#elif hour == 19 and mins > 30:
			#	return late
		
	# direct employees
	elif (salary > LOW_SALARY):
		# day shift
		if (shift == 'GS') or (shift == 'A SHIFT'):
			if hour > 9:
				return late
			elif hour == 9 and mins > 30:
				return late
	
	return 'P'