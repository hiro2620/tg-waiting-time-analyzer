from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

THERMOGRAPHY_CAPACITY = 1.5

BASE_TIME = datetime(2020, 7, 1, 7, 50) # t = 0
MAX_TIME_STEP = 60 * 40 # [sec]

STATIONS_CONF = {
	'海浜幕張': {'time':14 * 60, 'sd':125}, # [sec]
	'京成幕張': {'time':15 * 60, 'sd':140}, # [sec]
	'幕張': {'time':16 * 60, 'sd':140} # [sec]
}

# nop = Number Of People
TRAINS_CONF = [
	{
		'station':'海浜幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':100}, # 武蔵野線 海浜幕張行 0751着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':180},  # 武蔵野線 海浜幕張行 0806着
			{'arrival_time':datetime(2020, 7, 1, 7, 53), 'nop':90}, # 京葉線 蘇我行 0753着
			{'arrival_time':datetime(2020, 7, 1, 8, 1), 'nop':120},  # 京葉線 蘇我行 0801着
			{'arrival_time':datetime(2020, 7, 1, 8, 9), 'nop':70},  # 京葉線 蘇我行 0809着
		]#560
	},
	{
		'station':'京成幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 50), 'nop':80}, # 京成千葉線 ちはら台行 0750着
			{'arrival_time':datetime(2020, 7, 1, 7, 58), 'nop':130}, # 京成千葉線 千葉中央行 0758着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':100}, # 京成千葉線 ちはら台行 0806着
			{'arrival_time':datetime(2020, 7, 1, 7, 50), 'nop':110}, # 京成千葉線 京成津田沼行 0750着
			{'arrival_time':datetime(2020, 7, 1, 8, 1), 'nop':120}, # 京成千葉線/千原線 京成津田沼行 0801着
		]#480
	},
	{
		'station':'幕張',
		'trains':[
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':130}, # 総武線 千葉行 0751着
			{'arrival_time':datetime(2020, 7, 1, 8, 0), 'nop':110}, # 総武線 千葉行 0800着
			{'arrival_time':datetime(2020, 7, 1, 8, 6), 'nop':80}, # 総武線 千葉行 0806着
			{'arrival_time':datetime(2020, 7, 1, 7, 51), 'nop':90}, # 総武線 中野行 0751着
			{'arrival_time':datetime(2020, 7, 1, 7, 55), 'nop':120}, # 総武線 中野行 0755着
			{'arrival_time':datetime(2020, 7, 1, 7, 58), 'nop':130}, # 総武線 中野行 0758着
			{'arrival_time':datetime(2020, 7, 1, 8, 4), 'nop':60}, # 総武線 中野行 0804着
		]#730
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

		self.time_needed = time_needed # [sec]
		self.people_list = people_list
		self.time_needed = time_needed
		self.standard_deviation = standard_deviation
		self.station_name = station_name
		self.time_list = np.random.normal(
			loc   = self.time_needed,  # average
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
		passed_people = self.wating_people[:sec * pass_people_cnt]
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
passed_people_list = []
history_gate = []
history_waiting = []
history_passed = []

for t in range(0, MAX_TIME_STEP+1):
	print('t=' + str(t))
	people_at_gate = flow.get_people_instances(t)
	history_gate.append(len(people_at_gate))

	thermo.add_waiting_people(people_at_gate)
	passed_people = thermo.proceed_time(1)
	history_passed.append(len(passed_people))

	history_waiting.append(thermo.get_waiting_people_cnt())

	for p in passed_people:
		# print(p)
		p.set_arrival_time_doorway(t)
		# print(p)
		passed_people_list.append(p)

TICKS_MAJOR = [x for x in range(0, MAX_TIME_STEP + 1, 600)]
TICKS_MINOR = [x for x in range(0, MAX_TIME_STEP + 1, 60)]

FIG_SIZE = (10.0, 6.0)

# draw graph
fig = plt.figure(1, figsize=FIG_SIZE)
ax1 = fig.add_subplot()
ax1.plot(history_gate, linewidth=1)
# ax1.scatter(np.arange(0, MAX_TIME_STEP + 1), history_gate, s=15)

ax1.set_title('Number of People Arriving at the School Gate per Second')
ax1.set_xlabel('t[sec]')
ax1.set_ylabel('number')
ax1.axvline(33*60, color='red')
ax1.set_xticks(TICKS_MAJOR, minor=False)
ax1.set_xticks(TICKS_MINOR, minor=True)


fig = plt.figure(2, figsize=FIG_SIZE)
ax2 = fig.add_subplot()
ax2.plot(history_waiting, linewidth=1)
ax2.set_title('Number of People in Line')
# ax2.scatter(np.arange(0, MAX_TIME_STEP + 1), history_waiting, s=15)
ax2.set_xlabel('t[sec]')
ax2.set_ylabel('number')
ax2.axvline(33*60, color='red')
ax2.set_xticks(TICKS_MAJOR, minor=False)
ax2.set_xticks(TICKS_MINOR, minor=True)

fig = plt.figure(3, figsize=FIG_SIZE)
ax3 = fig.add_subplot()
ax3.plot(history_passed, linewidth=1)
# ax3.scatter(np.arange(0, MAX_TIME_STEP + 1), history_passed, s=15, marker='.')
ax3.set_title('Number of People Passing Through Thermography per Second')
ax3.set_xlabel('t[sec]')
ax3.set_ylabel('number')
ax2.axvline(33*60, color='red')
ax3.set_xticks(TICKS_MAJOR, minor=False)
ax3.set_xticks(TICKS_MINOR, minor=True)

x1 = [x.arrival_time_gate for x in passed_people_list]
y1 = [x.calc_wait_time() for x in passed_people_list]

fig = plt.figure(4, figsize=FIG_SIZE)
ax4 = fig.add_subplot()
ax4.scatter(x1,y1, s=15, alpha=1)
ax4.axvline(33*60, color='red')
ax4.set_title('Time to Wait in Line vs Time to Through School Gate')
ax4.set_xticks(TICKS_MAJOR, minor=False)
ax4.set_xticks(TICKS_MINOR, minor=True)

x2 = [x.arrival_time_gate for x in passed_people_list]
y2 = [x.arrival_time_doorway for x in passed_people_list]

fig = plt.figure(5, figsize=FIG_SIZE)
ax5 = fig.add_subplot()
ax5.scatter(x2,y2, s=16, alpha=1, marker='.')
ax5.set_title('Time to Through Thermography vs Time to Through School Gate')
x2_sub = np.arange(0, MAX_TIME_STEP + 1)
y2_sub = x2_sub
ax5.plot(x2_sub, y2_sub, alpha=0.5)
ax5.axhline(33*60, color='red')
ax5.axhline(35*60, color='red')
ax5.set_xticks(TICKS_MAJOR, minor=False)
ax5.set_xticks(TICKS_MINOR, minor=True)

plt.show()