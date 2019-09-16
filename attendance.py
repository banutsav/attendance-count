import os
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

# Constants
# Salary grade for labor
LOW_SALARY = 300

# Master attendance dictionary
days_dict = {}

# Write master attendance dict to csv
def writeMasterToCSV(output_path, salaryfile, dates):
	# Construct a dataframe for employee salaries
	df = pd.read_csv(salaryfile)
	# making new data frame with dropped NA values 
	df = df.dropna(axis = 0, how ='any')
	df.set_index('Employee Code', inplace=True)

	# Sort dates
	dates.sort(key = lambda date: datetime.strptime(date, '%d-%b'))
	print('Destination:',output_path)
	
	# Construct Header
	header = 'EmpNo,Name,Count,Salary,EmpType'
	for date in dates:
		header = header + ',' + date

	# Write out file header and contents	
	with open(output_path, 'w') as f:
		# Write header
		f.write(header + '\n')
		
		# Iterate over all the employees in the master dictionary
		for emp in days_dict:

			# Get values from each row of dictionary
			count = days_dict[emp]['count']
			name = days_dict[emp]['name']
			attendance = days_dict[emp]['attendance']
			# Get the daily salary for a person	
			salary = df.loc[emp,'Total Salary'] if emp in df.index else 0
			# Classify employee from salary
			emptype = 'indirect' if salary < LOW_SALARY else 'direct'

			# Initialize CSV file data row
			row = str(emp) + ',' + str(name) + ',' + str(count) + ',' + str(salary) + ',' + str(emptype)
		
			# Determine whether present or absent for the days
			for date in dates:
				status = ''
				# No entry recorded in file for that day
				if attendance.get(date) == None:
					status = 'X'
				# File entry present
				else:
					status = attendance[date]
				# Append status to row to be written
				row = row + ',' + status
			
			# Write row
			f.write(row + '\n')

	# Close output CSV file
	f.close()
	print('Writing out to file completed...')
	
# Create a master dictionary for each employe and their attendance across the dates
def countDailyAttendance(d, date):
	count = 0
	for x in d:
		# Get status and name of each employee
		status = d[x]['Status']
		name = d[x]['Name']

		# Update record for employee with empno = x
		if days_dict.get(x) == None:
			# Initialize employee entry
			days_dict[x] = {'count': 0, 'name': name, 'attendance': {}}
			
			# Check if keyword 'present' is in status
			if ('Present' in status):
				days_dict[x]['count'] = 1
				days_dict[x]['attendance'][date] = 'P' 
			else:
				days_dict[x]['attendance'][date] = 'A'
			
			# Count Number of employees inserted	 
			count = count + 1
		
		# Employee already present, no need to insert
		elif days_dict.get(x) != None:
			# Check if keyword 'present' is in status
			if ('Present' in status):
				days_dict[x]['count'] += 1
				days_dict[x]['attendance'][date] = 'P'
			else:
				days_dict[x]['attendance'][date] = 'A'

	if count > 0:
		print('Total employees inserted from file for',date,':',count)


# Get each file from the input folder and convert into a dictionary
def createEmpAttendanceDict(data_source):
	dates = []
	for filename in os.listdir(data_source):
		try:
			if filename.endswith('.csv') and not 'salary' in filename:
				# Get date from filename
				date = os.path.splitext(filename)[0]
				dates.append(date)
				# Get source file path
				file_path = Path(Path(data_source) / filename)
				# Create Data Frame
				df = pd.read_csv(file_path, index_col='E. Code', usecols=['E. Code', 'Name', 'Status'])
				d = df.to_dict('index')
				# Update master dictionary with attendances for that day
				countDailyAttendance(d, date)
		except Exception as e:
			print('[ERROR] There was an issue with file ' + filename + ', it will be skipped over')
			print(e)

	return dates

if __name__ == '__main__':

	try:
		print('Execution started...')
		data_source = Path(Path(os.getcwd()) / 'input')
		print('Source: ', data_source)
		dates = createEmpAttendanceDict(data_source)
		salaryfile = Path(Path(os.getcwd()) / 'input/salary-eid.csv')
		output_path = Path(Path(os.getcwd()) / 'output/attendance-count.csv')
		writeMasterToCSV(output_path, salaryfile, dates)

	except Exception as e:
		print('[ERROR]:',e)
	
	finally:
		print('Completed...')
		input('You can close this window now...')