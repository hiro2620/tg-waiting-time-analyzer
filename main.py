import numpy as np

class Train:

	def __init__(self, arrival_time, time_needed, People_list, standard_deviation=1, station_name=None):

		self.arrival_time = arrival_time
		self.time_needed = time_needed
		self.People_list = People_list
		self.time_needed = time_needed
		self.standard_deviation = standard_deviation
		self.station_name = station_name
		self.time_list = np.random.normal(
			loc   = self.arrival_time + self.time_needed,  # average
			scale = self.standard_deviation,               # standard deviation
			size  = len(self.People_list)                  # size of output
		)

		for P, t in zip(self.People_list, self.time_list):
			P.station2gate_t = t
			P.station_name = self.station_name
			P.arrival_time = self.arrival_time


	def get_people_cnt(self, time):
		return len(self.time_list <= time)


class PeopleFlow:

	def __init__(self, Train_list):

		self.Train_list = Train_list

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