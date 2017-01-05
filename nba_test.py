import sys
import os
import httplib
import datetime as dt

import xml.etree.ElementTree as ET
from workflow import Workflow


def get(wf):
	conn = httplib.HTTPSConnection("api.sportradar.us")

	# http://api.sportradar.us/nba-t3/games/2016/12/31/schedule.xml?api_key=mhptr4zdhsbdy39qwzq8cxds
    # query = query.split('$')
    # part = int(sys.argv[2])

    # TODO: check send request in 1 sec
	year = str(dt.datetime.now().year)
	month = str(dt.datetime.now().month)
	day = str(dt.datetime.now().day)

	if len(sys.argv) == 2:
		query = sys.argv[1]
		if len(query) == 8:
    		# TODO: check the valid of date
			year = query[0:4]
			month = query[4:6]
			day = query[6:8]


	if len(month) == 1:
		month = '0' + month
	if len(day) == 1:
		day = '0' + day

	date1 = year+"/"+month+"/"+day
	date2 = month+"-"+day+"-"+year
	date3 = year+""+month+""+day

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

