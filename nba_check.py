import sys
import urllib2
import datetime as dt

from workflow import Workflow
from BeautifulSoup import Comment
from BeautifulSoup import BeautifulSoup as BS


class Date:
	def __init__(self, year, month, day, valid):
		self.year = year
		self.month = month
		self.day = day
		self.valid = valid

class Team:
	def __init__(self, team):
		t = BS(team)
		divs = t.li.findAll('div', recursive=False)
		name = BS(str(divs[1]))
		fn = name.find('span', {'data-tst': 'first-name'})
		ln = name.find('span', {'data-tst': 'last-name'})
		self.firstName = fn.text
		self.lastName = BS(str(ln)).find('div').text
		self.short = findShort(self.firstName+' '+self.lastName)
		self.score = BS(str(divs[2])).text


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

def findShort(name):
	shorts = {'Boston Celtics'         : 'BOS',
			  'Brooklyn Nets'          : 'BKN',
			  'New York Knicks'        : 'NYK',
			  'Philadelphia 76ers'     : 'PHI',
			  'Toronto Raptors'        : 'TOR',
			  'Golden State Warriors'  : 'GSW',
			  'Los Angeles Clippers'   : 'LAC',
			  'Los Angeles Lakers'    : 'LAL',
			  'Phoenix Suns'           : 'PHX',
			  'Sacramento Kings'       : 'SAC',
			  'Chicago Bulls'          : 'CHI',
			  'Cleveland Cavaliers'    : 'CLE',
			  'Detroit Pistons'        : 'DET',
			  'Indiana Pacers'         : 'IND',
			  'Milwaukee Bucks'        : 'MIL',
			  'Dallas Mavericks'       : 'DAL',
			  'Houston Rockets'        : 'HOU',
			  'Memphis Grizzlies'      : 'MEM',
			  'New Orleans Pelicans'   : 'NOP',
			  'San Antonio Spurs'      : 'SAS',
			  'Atlanta Hawks'          : 'ATL',
			  'Charlotte Hornets'      : 'CHA',
			  'Miami Heat'             : 'MIA',
			  'Orlando Magic'          : 'ORL',
			  'Washington Wizards'     : 'WAS',
			  'Denver Nuggets'         : 'DEN',
			  'Minnesota Timberwolves' : 'MIN',
			  'Oklahoma City Thunder'  : 'OKC',
			  'Portland Trail Blazers' : 'POR',
			  'Utah Jazz'              : 'UTA'}
	
	if name in shorts:
		return shorts[name]

	return 'blank'

def get(wf):

	wf = Workflow()

	query = sys.argv[1]
	date = getDate(query)
	
	if date.valid == 0:
		wf.add_item(title = "can't recognize the input")
		wf.send_feedback()
		return 

	year = date.year
	month = date.month
	day = date.day

	if len(month) == 1:
		month = '0' + month
	if len(day) == 1:
		day = '0' + day

	date1 = year+"-"+month+"-"+day
	date2 = year+""+month+""+day

	url = 'http://sports.yahoo.com/nba/scoreboard/?dateRange='+date1
	html = urllib2.urlopen(url)
	soup = BS(html)

	comments = soup.findAll(text=lambda text:isinstance(text, Comment))
	[comment.extract() for comment in comments]

	games = soup.findAll('div', {'class': 'Px(20px) Py(10px)'})

	num = str(len(games))
	wf.add_item(title = num + " games on " + date1)

	for game in games:
		# search time
		g = BS(str(game))
		status = g.find('span').text

		gameInfo = g.findAll('div', {'class': 'score'})
		teams = BS(str(gameInfo)).findAll('li')
		# print(len(teams))

		away = Team(str(teams[0]))
		home = Team(str(teams[1]))

		icon_url = 'image/' + home.short + '.png'
		title = home.short + ' vs ' + away.short 

		info = None
		if len(home.score.split('-')) == 1:
			info = home.firstName + ' ' + home.lastName + ' ' + \
				   home.score + ' : ' + away.score + ' ' + \
			   	   away.firstName + ' ' + away.lastName
			info = "{:<70}".format(info) + status
		else:
			info = home.firstName + ' ' + home.lastName + ' (' + home.score + ')'\
				   + ' vs ' + \
			   	   away.firstName + ' ' + away.lastName + ' (' + away.score + ')'
			info = "{:<70}".format(info) + status


		# print(title)
		# print(info)

		wf.add_item(title = title,
					subtitle = info,
					icon  = icon_url)
	wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(get))


