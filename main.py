#!/usr/bin/env python3.8

import curses
from curses.textpad import rectangle
import requests
import csv
import os
import pickle

#################
# Data structures
#################

"""
Representation of portfolio
"""
class portfolio:
	"""
	Load 
	"""
	def __init__(self, data):
		self.name = data[0]
		self.init_val = data[1]
		self.maker_fee = data[2]
		self.taker_fee = data[3]
		self.long_positions = []
		self.short_positions = []
		self.closed_positions = []
		self.opened_price_date = -1
		self.closed_price_date = -1
		

	def load_opened(self):
		self.long_positions = []
		script_dir = os.path.dirname(__file__)
		with open(os.path.join(script_dir, "portfolios", self.name, "long_positions.txt")) as opened_positions_csv:
			csv_reader = csv.reader(opened_positions_csv, delimiter=',')
			line_count = 0
			for line in csv_reader:
				line_count += 1
				if (line_count == 1):
					continue
				self.long_positions.append(opened_position(line))

		self.short_positions = []
		with open(os.path.join(script_dir, "portfolios", self.name, "short_positions.txt")) as opened_positions_csv:
			csv_reader = csv.reader(opened_positions_csv, delimiter=',')
			line_count = 0
			for line in csv_reader:
				line_count += 1
				if (line_count == 1):
					continue
				self.short_positions.append(opened_position(line))
		

	def load_closed(self):
		self.closed_positions = []
		script_dir = os.path.dirname(__file__)
		with open(os.path.join(script_dir, "portfolios", self.name, "closed_positions.txt")) as opened_positions_csv:
			csv_reader = csv.reader(opened_positions_csv, delimiter=',')
			line_count = 0
			for line in csv_reader:
				line_count += 1
				if (line_count == 1):
					continue
				self.closed_positions.append(opened_position(line))


"""
Class represents opened position.
"""
class opened_position:
	def __init__(self, data):
		self.name = data[0]
		self.ref_coin = data[1]
		self.init_price = float(data[2])
		self.init_value = float(data[3])
		self.curr_price = -1
		self.curr_value = -1
		self.percent = -1


	def load_current_price(self):
		URL = "https://api.binance.com/api/v1/ticker/price?symbol={}{}".format(self.name, self.ref_coin)
		page = requests.get(URL)
		
		self.curr_price = float(page.json()["price"])
		self.curr_value = (self.init_value / self.init_price) * self.curr_price
		self.percent = self.curr_price / (self.init_price / 100.0) - 100.0
		

	def print_position(self, stdscr, x, y, index):
		color = 5 if (self.percent > 0) else 3
		fst_half = "{}){:>6}/{:<6}{:>10.2f}{:>10}".format(index + 1, self.name, self.ref_coin, self.init_value, self.init_price)

		snd_half = "{:>10.2f}{:>10}{:10.2f}".format(self.curr_value, self.curr_price, self.percent)
		
		stdscr.insstr(y, x, fst_half)
		stdscr.attron(curses.color_pair(color))
		stdscr.insstr(y, x + len(fst_half), snd_half)
		stdscr.attroff(curses.color_pair(color))


	def print_detailed_info(self, stdscr, x, y):
		pass


"""
Class represents closed position.
"""
class closed_position:
	def __init__(self, data):
		self.name = data[0]
		self.ref_coin = data[1]
		self.init_price = float(data[2])
		self.init_value = float(data[3])
		self.close_price = float(data[4])
		self.close_value = float(data[5])
		self.profit = float(data[6])
		self.profit_percent = float(data[7])
		self.open_date = data[8]
		self.close_date = data[9]
		self.percent_since = -1


	def load_current_price(self):
		URL = "https://api.binance.com/api/v1/ticker/price?symbol={}{}".format(self.name, self.ref_coin)
		page = requests.get(URL)
		self.percent_since = float(page.json()["price"]) / (self.init_price / 100.0) - 100.0


	def print_position(self, stdscr, x, y):
		pass


	def print_detailed_info(self, stdscr, x, y):
		pass


###########
# Functions
###########


# GUI handling

"""
Print header for active tab.

args:
	stdscr = curses screen
	tab_idx = index of active tab
	menu = list of tabs
	w = window width
"""
def print_header(stdscr, tab_idx, menu, w):
	x = 0
	y = 0
	header_init = "Invest tracker 1.0 |"
	header_delimiter = "|"

	stdscr.attron(curses.color_pair(1))
	stdscr.addstr(y, x, " " * w)
	stdscr.addstr(y, x, header_init)
	x = len(header_init)

	for idx, row in enumerate(menu):
		if idx == tab_idx:
			stdscr.attroff(curses.color_pair(1))
			stdscr.addstr(y, x, " " + row + " ")
			stdscr.attron(curses.color_pair(1))
		else:
			stdscr.addstr(y, x, " " + row + " ")
		x += len(row) + 2

		stdscr.addstr(y, x, header_delimiter)
		x += len(header_delimiter)
	stdscr.attroff(curses.color_pair(1))
	stdscr.refresh()


"""
Print footer for active tab.

args:
	stdscr - curses screen
	tab_idx - index of active tab
	w - window width
	h - window heigth
"""
def print_footer(stdscr, tab_idx, w, h):
	x = 0
	y = h - 1
	stdscr.attron(curses.color_pair(1))
	stdscr.insstr(y, x, " " * w)

	if (tab_idx == 0):
		stdscr.insstr(y, x, " <q> - Exit | <Enter> - select item | <r> - refresh data | <a> - add position")
	elif (tab_idx == 1):
		stdscr.insstr(y, x, " <q> - Exit | <Enter> - select item | <r> - refresh data | <a> - add position")
	elif (tab_idx == 2):
		stdscr.insstr(y, x, " <q> - Exit | <Enter> - select item")
	elif (tab_idx == 3):
		stdscr.insstr(y, x, " <q> - Exit | <Enter> - select item | <e> - edit portfolio")

	stdscr.attroff(curses.color_pair(1))
	stdscr.refresh()


# Opened positions tab


def add_position(stdscr, h, w, portfolio):
	selected_field = 0
	field_count = 6
	fields = ["Coin =", "Reference coin =", "Initial value =", "Initial price =", " Submit ", " Cancel "]
	field_values = ["","","",""]

	while True:
		stdscr.clear()
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(0, 0, " " * w)
		stdscr.addstr(0, 0, "Add Long Position")
		stdscr.attroff(curses.color_pair(1))
		x = 3
		if selected_field == 0:
			stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[0])
		stdscr.attroff(curses.color_pair(1))
		stdscr.addstr(x, 3+len(fields[0])+2, field_values[0])
		rectangle(stdscr, x-1,3+len(fields[0])+1, x+1, 40)

		x = 7
		if selected_field == 1:
			stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[1])
		stdscr.attroff(curses.color_pair(1))
		stdscr.addstr(x, 3+len(fields[1])+2, field_values[1])
		rectangle(stdscr, x-1,3+len(fields[1])+1, x+1, 40)

		x = 11
		if selected_field == 2:
			stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[2])
		stdscr.attroff(curses.color_pair(1))
		stdscr.addstr(x, 3+len(fields[2])+2, field_values[2])
		rectangle(stdscr, x-1,3+len(fields[2])+1, x+1, 40)

		x = 15
		if selected_field == 3:
			stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[3])
		stdscr.attroff(curses.color_pair(1))
		stdscr.addstr(x, 3+len(fields[3])+2, field_values[3])
		rectangle(stdscr, x-1,3+len(fields[3])+1, x+1, 40)
		
		x = 19
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[4])
		stdscr.addstr(x, 6+len(fields[4]), fields[5])
		stdscr.attroff(curses.color_pair(1))
		if selected_field == 4:
			rectangle(stdscr, x-1, 2, x+1, 3+len(fields[4]))
		elif selected_field == 5:
			rectangle(stdscr, x-1, 5+len(fields[4]), x+1, 6+len(fields[4])+len(fields[5]))

		key = stdscr.getch()
		if key == curses.KEY_UP:
			selected_field = (selected_field - 1) % field_count
			continue
		elif key == curses.KEY_DOWN or key == 9:
			selected_field = (selected_field + 1) % field_count
			continue
		elif key == curses.KEY_ENTER or key == 10 or key == 13:
			if selected_field == 4:
				portfolio.long_positions.append(opened_position([field_values[0].upper(), field_values[1].upper(), float(field_values[3]), float(field_values[2])]))
				break
			elif selected_field == 5:
				break
			else:
				selected_field = (selected_field + 1) % field_count
				continue
		elif selected_field < 4:
			if key == 127:
				field_values[selected_field] = field_values[selected_field][:-1]
			else:
				field_values[selected_field] += chr(key)


def close_position(stdscr, h, w, portfolio):
	selected_field = 0
	field_count = 3
	fields = ["Index =", " Submit ", " Cancel "]
	field_values = [""]

	while True:
		stdscr.clear()
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(0, 0, " " * w)
		stdscr.addstr(0, 0, "Remove Long Position")
		stdscr.attroff(curses.color_pair(1))
		x = 3
		if selected_field == 0:
			stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[0])
		stdscr.attroff(curses.color_pair(1))
		stdscr.addstr(x, 3+len(fields[0])+2, field_values[0])
		rectangle(stdscr, x-1,3+len(fields[0])+1, x+1, 40)
		
		x = 7
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(x, 3, fields[1])
		stdscr.addstr(x, 6+len(fields[2]), fields[2])
		stdscr.attroff(curses.color_pair(1))
		if selected_field == 1:
			rectangle(stdscr, x-1, 2, x+1, 3+len(fields[1]))
		elif selected_field == 2:
			rectangle(stdscr, x-1, 5+len(fields[1]), x+1, 6+len(fields[1])+len(fields[2]))

		key = stdscr.getch()
		if key == curses.KEY_UP:
			selected_field = (selected_field - 1) % field_count
			continue
		elif key == curses.KEY_DOWN or key == 9:
			selected_field = (selected_field + 1) % field_count
			continue
		elif key == curses.KEY_ENTER or key == 10 or key == 13:
			if selected_field == 1:
				del portfolio.long_positions[int(field_values[0]) - 1]
				break
			elif selected_field == 2:
				break
			else:
				selected_field = (selected_field + 1) % field_count
				continue
		elif selected_field < 1:
			if key == 127:
				field_values[selected_field] = field_values[selected_field][:-1]
			else:
				field_values[selected_field] += chr(key)


"""
"""
def tab_opened_pos(stdscr, tab_idx, menu, key, h, w, portfolio):
	x = 0
	min_y = 4
	max_y = h - 3

	if key in [65, 97]: # <a> - add position
		add_position(stdscr, h, w, portfolio)
		stdscr.clear()
	elif key in [68, 100]:
		close_position(stdscr, h, w, portfolio)
		stdscr.clear()

	print_header(stdscr, tab_idx, menu, w)
	print_footer(stdscr, tab_idx, w, h)
	
	if (len(portfolio.long_positions) > 0):
		stdscr.insstr(min_y - 2, x, "Long Positions:")
		stdscr.insstr(min_y - 1, x, "{}{:^13}{:>10}{:>10}{:>10}{:>10}{:>10}"
		.format("ID", "Pair name", "I. Val", "I. Price", "C. Val", "C. Price", "Percent"))
	else:
		stdscr.insstr(min_y - 2, x, "No opened long positions.")

	if (len(portfolio.short_positions) > 0):
		stdscr.insstr(min_y + len(portfolio.long_positions) + 1, x, "Long Positions:")
		stdscr.insstr(min_y + len(portfolio.long_positions) + 2, x, "{}{:^13}{:>10}{:>10}{:>10}{:>10}{:>10}"
		.format("ID", "Pair name", "I. Val", "I. Price", "C. Val", "C. Price", "Percent"))
	else:
		stdscr.insstr(min_y + len(portfolio.long_positions) + 1, x, "No opened short positions.")

	stdscr.refresh()

	if key in [82, 114]: # <r> - refresh
		for i, long_position in enumerate(portfolio.long_positions):
			long_position.load_current_price()
			long_position.print_position(stdscr, 0, min_y + i, i)
			stdscr.refresh()

		for i, short_position in enumerate(portfolio.short_positions):
			short_position.load_current_price()
			short_position.print_position(stdscr, 0, min_y + len(portfolio.long_positions) + 2 + i, i)
			stdscr.refresh()

	else:
		for i in range(len(portfolio.long_positions)):
			portfolio.long_positions[i].print_position(stdscr, 0, min_y + i, i)

		for i in range(len(portfolio.short_positions)):
			portfolio.short_positions[i].print_position(stdscr, 0, min_y + len(portfolio.long_positions) + 2 + i, i)
		stdscr.refresh()


# Favourite positions tab

"""
"""
def tab_favourite_pos(stdscr, tab_idx, menu, key, h, w, portfolio):
	print_header(stdscr, tab_idx, menu, w)
	print_footer(stdscr, tab_idx, w, h)


# Sweetspot finder tab

"""
"""
def tab_sweetspot_find(stdscr, tab_idx, menu, key, h, w, portfolio):
	print_header(stdscr, tab_idx, menu, w)
	print_footer(stdscr, tab_idx, w, h)


# Account overview tab

"""
"""
def tab_acc_overview(stdscr, tab_idx, menu, key, h, w, portfolio):
	print_header(stdscr, tab_idx, menu, w)
	print_footer(stdscr, tab_idx, w, h)


# Portfolio manipulation

#Not needed anymore
"""
def import_portfolios():
	portfolios = []
	script_dir = os.path.dirname(__file__)
	selected_portfolio = 0
	with open(os.path.join(script_dir, "portfolios.txt")) as portfolio_csv:
		csv_reader = csv.reader(portfolio_csv, delimiter=',')
		index = 0
		for line in csv_reader:
			index += 1
			if index == 1:
				continue
			portfolios.append(portfolio(line))

	for index in range(len(portfolios)):
		portfolios[index].load_opened()
		portfolios[index].load_closed()

	return portfolios, selected_portfolio
"""


"""
Create new portfolio and append it to given list.

Args:
	portfolios - list of existing portfolios
"""
def create_portfolio(portfolios):
	pass


"""
Remove portfolio from given list.

Args:
	portfolios - list of existing portfolios
"""
def delete_portfolio(portfolios):
	pass


"""
Load porfolio from pickle file. If not exist, create new porfolio and saves it.

Args:
	file_path - path to file where are portfolios stored

Returns:
	portfolios - list of portfolios
	selected_portfolio - currently shown portfolio
"""
def load_portfolios(file_path):
	try:
		portfolios, selected_portfolio = pickle.load(open(file_path, "rb"))
	except (OSError, IOError):
		portfolios = []
		selected_portfolio = 0
		create_portfolio(portfolios)
		pickle.dump([portfolios, selected_portfolio], open(file_path, "wb"))
	
	return portfolios, selected_portfolio


"""
Defines behavior of main menu.

Args:
	stdscr - standard screen for curses
"""
def main_menu(stdscr):
	# turn off cursor blinking
	curses.curs_set(0)

	# color scheme for selected row
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.init_pair(2, curses.COLOR_RED, curses.COLOR_WHITE)
	curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
	curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_WHITE)
	curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)

	#check window size
	h, w = stdscr.getmaxyx()
	if h < 25 or w < 100:
		return 1
	
	file_path = os.path.join(os.path.dirname(__file__), "portfolios.p")

	# main menu
	menu = ['Opened positions', 'Favourite positions', 'Sweetspot finder', 'Portfolio overview']
	print_tab = [tab_opened_pos, tab_favourite_pos, tab_sweetspot_find, tab_acc_overview]
	tab_idx = 0
	tab_count = len(menu)
	key = 0
	portfolios, selected_portfolio = load_portfolios(file_path)

	while True:
		stdscr.clear()
		print_tab[tab_idx](stdscr, tab_idx, menu, key, h, w, portfolios[selected_portfolio])

		key = stdscr.getch()

		if key == curses.KEY_LEFT:
			tab_idx = (tab_idx - 1) % tab_count
			continue
		elif key == curses.KEY_RIGHT or key == 9:
			tab_idx = (tab_idx + 1) % tab_count
			continue
		elif key in [81, 113]: # <q> - Exit
			pickle.dump([portfolios, selected_portfolio], open(file_path, "wb"))
			break
	return 0


"""
MAIN
"""
if __name__ == "__main__":
	if curses.wrapper(main_menu) == 1:
		print("Minimal size of terminal window is 100x25!")
