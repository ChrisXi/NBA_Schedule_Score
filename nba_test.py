import sys
import os
import httplib
import time
import datetime as dt

import xml.etree.ElementTree as ET
from workflow import Workflow
from plistlib import readPlist, writePlist

class Date:
	def __init__(self, year, month, day, valid):
		self.year = year
		self.month = month
		self.day = day
		self.valid = valid

def getDate(query):
	
	date = dt.datetime.now()
	
	valid = 0

	year  = None
	month = None
	day  = None

	if len(query) == 0:
		valid = 1
	elif len(query) == 1:
		if query == "y":
			date = date - dt.timedelta(days = 1)
			valid = 1
		elif query == "t":
			date = date + dt.timedelta(days = 1)
			valid = 1
		else:
			if query.isdigit() and query != "0":
				day = query
				valid = 1
	else:
		if query[0] == "+" or query[0] == "-":
			days = query[1:]
			if days.isdigit():
				if query[0] == "+":
					date = date + dt.timedelta(days = int(days))
				else:
					date = date - dt.timedelta(days = int(days))
				valid = 1
		else:
			ymd = query.split()
			if len(ymd) == 1:
				if ymd[0].isdigit():
					day = ymd[0]
					valid = 1
			elif len(ymd) == 2:
				if ymd[0].isdigit() and ymd[1].isdigit():
					month = ymd[0]
					day = ymd[1]
					valid = 1
				elif ymd[0] == "set":
					info = readPlist('info.plist')
					info['API_KEY'] = 'ABC-XYZ'
					valid = 2
			elif len(ymd) == 3:
				if ymd[0].isdigit() and ymd[1].isdigit() and ymd[2].isdigit():
					year = ymd[0]
					month = ymd[1]
					day = ymd[2]
					valid = 1

	if valid == 1:
		if year == None:
			year = str(date.year)
		if month == None:
			month = str(date.month)
		if day == None:	
			day = str(date.day)

		valid = validDate(year, month, day)

	return Date(year, month, day, valid)

def validDate(year, month, day):
	valid = 1
	try:
		bb = dt.datetime(year=int(year),month=int(month),day=int(day))
	except ValueError:
		valid = 0

	return valid

def get(wf):

	api_key = os.getenv("API_KEY")
	wf.add_item(title = str(api_key))
	wf.send_feedback()
	return 

	conn = httplib.HTTPSConnection("api.sportradar.us")

	# http://api.sportradar.us/nba-t3/games/2016/12/31/schedule.xml?api_key=mhptr4zdhsbdy39qwzq8cxds
	
	query = sys.argv[1]
	date = getDate(query)
	
	if date.valid == 0:
		wf.add_item(title = "can't recognize the input")
		wf.send_feedback()
		return 
	elif date.valid == 2:
		wf.add_item(title = "API key was set")
		wf.send_feedback()
		return

	year = date.year
	month = date.month
	day = date.day

	if len(month) == 1:
		month = '0' + month
	if len(day) == 1:
		day = '0' + day

	date1 = year+"/"+month+"/"+day
	date2 = month+"-"+day+"-"+year
	date3 = year+""+month+""+day

	time.sleep(.200)

	request = "/nba-t3/games/"+date1+"/schedule.xml?api_key=mhptr4zdhsbdy39qwzq8cxds"
	conn.request("GET", request)
	res = conn.getresponse()
	data = res.read()

	# print(data.decode("utf-8"))

	wf = Workflow()
	root = ET.fromstring(data)

	# TODO: check if exist
	num = str(len(root[0][0]))

	wf.add_item(title = num + " games on " + date2)

	for game in root[0][0]:	
		# print(game.attrib['status'])
		status = game.attrib['status']
		home = game[1].attrib['alias']
		away = game[2].attrib['alias']
		home_points = '0'
		away_points = '0'

		if status != 'scheduled':
			if 'home_points' in game.attrib and 'away_points' in game.attrib:
				home_points = game.attrib['home_points'];
				away_points = game.attrib['away_points'];

		info = home + " (" + home_points + ")" + " : " + away + " (" + away_points + ")"
		# print(info)

		return_url = "http://www.nba.com/games/"+date3+"/"+away+home
		icon_url   = "image/" + home + ".png"
		wf.add_item(title = info,
					icon  = icon_url,
					arg   = return_url,
					valid = True)
	wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(get))


