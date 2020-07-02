from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

THERMOGRAPHY_CAPACITY = 1

BASE_TIME = datetime(2020, 7, 1, 7, 50) # t = 0
MAX_TIME_STEP = 60 * 40 # [sec]

STATIONS_CONF = {
	'海浜幕張': {'time':15 * 60, 'sd':240}, # [sec]
	'京成幕張': {'time':17 * 60, 'sd':250}, # [sec]
	'幕張': {'time':18 * 60, 'sd':260} # [sec]
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
			{'arrival_time':datetime(2020, 7, 1, 8, 1), 'nop':300}, # 京成千葉線 ちはら台行 0806着
			{'arrival_time':datetime(2020, 7, 1, 7, 50), 'nop':300}, # 京成千葉線 京成津田沼行 0750着
			{'arrival_time':datetime(2020, 7, 1, 8, 1), 'nop':300}, # 京成千葉線/千原線 京成津田沼行 0801着
		]
	},
	{
		'station':'幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':300}, # 総武線 千葉行 0751着
			{'arrival_time':datetime(2020, 7, 1, 8, 0), 'nop':300}, # 総武線 千葉行 0800着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':300}, # 総武線 千葉行 0806着
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':300}, # 総武線 中野行 0751着
			{'arrival_time':datetime(2020, 7, 1, 7, 55), 'nop':300}, # 総武線 中野行 0755着
			{'arrival_time':datetime(2020, 7, 1, 7, 58), 'nop':300}, # 総武線 中野行 0758着
			{'arrival_time':datetime(2020, 7, 1, 8, 4), 'nop':300}, # 総武線 中野行 0804着
		]
	}
]


class People:

	def __init__(self):
		self.arrival_time_station = None
		self.arrival_time_gate = None
		self.arrival_time_doorway = None


	def set_arrival_time_station(self, sec):
		self.arrival_time_station = sec # seconds


	def set_arrival_time_gate(self, station2gate_sec):
		assert self.arrival_time_station is not None, 'Run set_arrival_time_station() first.'
		self.arrival_time_gate = self.arrival_time_station + station2gate_sec


	def set_arrival_time_doorway(self, sec):
		assert self.arrival_time_gate is not None, 'Run set_arrival_time_gate() first.'
		self.arrival_time_doorway = sec


	def calc_wait_time(self):
		return self.arrival_time_doorway - self.arrival_time_gate # [sec]



class Train:

	def __init__(self, base_time, arrival_time, time_needed, people_list, standard_deviation=1, station_name=None):
		assert isinstance(base_time, datetime), 'base_time must be an instance of datetime.datetime'
		assert isinstance(arrival_time, datetime), 'arrival_time must be an instance of datetime.datetime'
		self.arrival_time = (arrival_time - base_time).total_seconds() # [sec] <class 'datetime.timedelta'> -> float
		print(self.arrival_time)

		self.time_needed = time_needed # [sec]
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
			p.set_arrival_time_gate(t)


	def get_people_cnt(self, time):
		return len(self.time_list <= time)


	def get_people_instance(self, time):
		return [p for p in self.people_list if time - 1 <= p.arrival_time_gate < time]



class PeopleFlow:

	def __init__(self, trains_list):
		self.trains_list = trains_list


	def get_people_cnt(self, time):
		cnt = 0
		for train in self.trains_list:
			cnt += train.get_people_cnt(time)

		return cnt


	def get_people_instances(self, time):
		people = []
		for train in self.trains_list:
			people.extend(train.get_people_instance(time))

		return people



class ThermographyLine:

	def __init__(self, cnt_per_sec):
		self.cnt_per_sec = cnt_per_sec
		self.wating_people = []

	def add_waiting_people(self, people_instance):
		self.wating_people.extend(people_instance)

	def proceed_time(self, sec):
		pass_people_cnt = round(sec * self.cnt_per_sec)
		passed_people = self.wating_people[:sec * pass_people_cnt - 1]
		self.wating_people = self.wating_people[sec * pass_people_cnt:]
		return passed_people

	def get_waiting_people_cnt(self):
		return len(self.wating_people)





### main ###

# create train instances
trains_list = []
for data in TRAINS_CONF:
	station_name = data['station']

	for train in data['trains']:
		# create people instances
		people_list = []
		for p in range(0, train['nop']):
			people_list.append(People())

		trains_list.append(
			Train(
				BASE_TIME,
				train['arrival_time'],
				STATIONS_CONF[station_name]['time'],
				people_list,
				STATIONS_CONF[station_name]['sd'],
				station_name
				)
		)

flow = PeopleFlow(trains_list)
thermo = ThermographyLine(THERMOGRAPHY_CAPACITY)

# main loop
time_step = 0 # [sec]

passed_people = []
history_gate = []
history_waiting = []
history_passed = []

for t in range(0, MAX_TIME_STEP):
	people_at_gate = flow.get_people_instances(t)
	history_gate.append(len(people_at_gate))

	thermo.add_waiting_people(people_at_gate)
	passed_people = thermo.proceed_time(1)
	history_passed.append(len(passed_people))

	history_waiting.append(thermo.get_waiting_people_cnt())

	for p in passed_people:
		p.set_arrival_time_doorway(t)
		passed_people.append(p)

# draw graph
fig = plt.figure()

ax1 = fig.add_subplot(2,2,1)
ax1.plot(history_gate)

ax2 = fig.add_subplot(2,2,2)
ax2.plot(history_waiting)

ax3 = fig.add_subplot(2,2,3)
ax3.plot(history_passed)

plt.show()