from datetime import datetime, timedelta
import numpy as np

THERMOGRAPHY_CAPACITY = 1

STATIONS_CONF = {
	'海浜幕張': {'time':15, 'sd':1},
	'京成幕張': {'time':17, 'sd':1},
	'幕張': {'time':18, 'sd':1}
}

# nop = Number Of People
TRAINS_CONF = [
	{
		'station':'海浜幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':300}, # 武蔵野線 海浜幕張行 0751着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':300},  # 武蔵野線 海浜幕張行 0806着
			{'arrival_time':datetime(2020, 7, 1, 7, 53), 'nop':300}, # 京葉線 蘇我行 0753着
			{'arrival_time':datetime(2020, 7, 1, 8, 1), 'nop':300},  # 京葉線 蘇我行 0801着
			{'arrival_time':datetime(2020, 7, 1, 8, 9), 'nop':300},  # 京葉線 蘇我行 0809着
			{'arrival_time':datetime(2020, 7, 1, 8, 12), 'nop':300},  # 京葉線 蘇我行 0812着
		]
	},
	{
		'station':'京成幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 50), 'nop':300}, # 京成千葉線 ちはら台行 0750着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':300}, # 京成千葉線 ちはら台行 0806着
		]
	},
	{
		'station':'幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':300}, # 総武線 千葉行 0751着
			{'arrival_time':datetime(2020, 7, 1, 8, 0), 'nop':300}, # 総武線 千葉行 0800着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':300}, # 総武線 千葉行 0806着
		]
	}
]

class People:

	def __init__(self):
		self.arrival_time_station = None
		self.arrival_time_gate = None
		self.arrival_time_doorway = None

	def set_arrival_time_station(self, time):
		self.arrival_time_station = time

	def set_arrival_time_gate(self, minutes):
		assert self.arrival_time_station, 'Run set_arrival_time_station() first.'
		self.arrival_time_gate = self.arrival_time_station + timedelta(minutes=minutes)

	def set_arrival_time_doorway(self, time):
		assert self.arrival_time_gate, 'Run set_arrival_time_gate() first.'
		self.arrival_time_doorway = time

	def calc_wait_time(self):
		return (self.arrival_time_doorway - self.arrival_time_gate).total_seconds()


class Train:

	def __init__(self, arrival_time, time_needed, people_list, standard_deviation=1, station_name=None):

		self.arrival_time = arrival_time
		self.time_needed = time_needed
		self.people_list = people_list
		self.time_needed = time_needed
		self.standard_deviation = standard_deviation
		self.station_name = station_name
		self.time_list = np.random.normal(
			loc   = self.arrival_time + self.time_needed,  # average
			scale = self.standard_deviation,               # standard deviation
			size  = len(self.people_list)                  # size of output
		)

		for p, t in zip(self.people_list, self.time_list):
			p.set_arrival_time_station(self.arrival_time)
			p.set_arrival_time_gate(self.time_needed)



	def get_people_cnt(self, time):
		return len(self.time_list <= time)


class PeopleFlow:

	def __init__(self, Trains_list):

		self.Trains_list = Train_list

	def get_people_cnt(self, time):
		cnt = 0
		for Train in self.Train_list:
			cnt += Train.get_people_cnt(time)


class ThermographyLine:

	def __init__(self, cnt_per_sec):
		self.cnt_per_sec = cnt_per_sec
		self.wating_cnt = 0

	def add_wating_people(self, cnt):
		self.wating_cnt += cnt

	def proceed_time(self, sec):
		self.wating_cnt -= sec * self.cnt_per_sec
		if self.wating_cnt < 0:
			self.wating_cnt = 0


### main ###

# create train instances
trains_list = []
for data in TRAINS_CONF:
	station_name = data['station']

	for train in data['trains']:
		# create people instances
		people_list = []
		for p in range(0, train['nop']):
			people.append(People())

		trains_list.append(
			Train(
				train['arrival_time'],
				STATIONS_CONF[station_name]['time'],
				people_list,
				STATIONS_CONF[station_name]['sd'],
				station_name
				)
		)

flow = PeopleFlow(trains_list)