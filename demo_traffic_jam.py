# Date: 11/30
# Add reaction time after detecting gap_safe
# Add car's object

from vpython import *
from math import cos, sin, pi
import random
from random import seed
seed(0)
import numpy as np

def km_to_m(x):
	return x/3.6

def m_to_km(x):
	return 3.6*x

def to_degree(x):
	return x/circular_radius

def to_length(degree):
	return degree*circular_radius

def set_initial_position(car_id):
	return - interval*(car_id + (random.random()-0.5)*0.125*0.1)

def get_color(car_id = 0, speed = 0, use_speed_color = True):
	if use_speed_color:
		max_speed = km_to_m(108)
		if speed < km_to_m(20): return vec(1, 0, 0)
		elif speed < km_to_m(30): return vec(1, 0.5, 0)
		elif speed < km_to_m(45): return vec(1, 1, 0)
		elif speed < km_to_m(60): return vec(0.2, 1, 0.2)
		elif speed < km_to_m(80): return vec(0, 1, 0.6)
		else: return vec(0, 0.5, 1)	
	else:
		if car_id == 0: return color.red
		elif car_id == 1: return color.green
		elif car_id % 2: return color.yellow
		else: return color.blue
	
def output_situation(output_number = 4, output_ave_speed = True, output_speed = True, output_position = True, output_gap = True):
	print("T = %.2f" %t)
	average_speed = m_to_km(np.mean(np.array([car.speed for car in cars])))
	if output_ave_speed: print('Average speed of all cars = %.2f (km/h)' %average_speed)
	if output_speed:
		print('Speed(km/h) =', end = ' ')
		for i in range(output_number): print("%.2f" %m_to_km(cars[i].speed), end="\t")
		print()
	if output_position:
		print('Theta(degree)=', end = ' ')
		for i in range(output_number): print("%.2f" %((cars[i].theta)/2/pi*360), end="\t")
		print()
	if output_gap:
		print('Gap(m)      =', end = ' ')
		for i in range(output_number): print("%.2f" %(cars[i].save_gap), end="\t")
		print()
	print('error_count =', error_count, '\n')

class Cars_obj(sphere):
	def __init__(self, car_id, version = 1):
		self.theta = set_initial_position(car_id) # initial position
		self.min_speed = 0   		# (meter/sec)
		self.max_speed = km_to_m(108)
		self.max_accel = 0.3 		# (meter/sec^2)
		self.max_decel = 3
		self.speed = random.gauss(mu = km_to_m(initial_mean_speed), sigma = km_to_m(initial_mean_speed)*0.125*0.2) # initial speed, gaussian distribution
		#self.speed = km_to_m(50) * (1 + (random.random()-0.5) * 0.5)	# uniform distribution 
		#self.compute_save_gap()
		sphere.__init__(self, pos = circular_radius * vec(cos(self.theta), sin(self.theta), 0), 
						radius = 1.5, color = get_color(car_id, self.speed, use_speed_color)) # for car's visualization
		
class Cars_human_driver(Cars_obj):
	def __init__(self, car_id, version = 1):
		super().__init__(car_id)
		if version == 1: # Eating
			self.decel = random.gauss(mu = 1.5,  sigma = 1.5*0.125)
			#self.accel = random.gauss(mu = 0.15, sigma = 0.15*0.125)
			self.accel = self.decel * 0.5
			self.decel = min(max(0, self.decel), self.max_decel)
			self.accel = min(max(0, self.accel), self.max_decel * 0.5)
			self.reaction_time_accel = min(random.gauss(mu = 2.0, sigma = 2.0*0.125), max_idle_time) # max = 5 sec, default mu = 3
			self.reaction_time_decel = self.reaction_time_accel * 0.5
			#self.reaction_time_decel = random.gauss(mu = 1.5, sigma = 1.5*0.125)
		elif version == 2: 
			self.accel = random.gauss(mu = 0.3*9.8/2.0, sigma = 0.03*9.8)
			self.decel = random.gauss(mu = 0.5*9.8/2.0, sigma = 0.03*9.8)
			self.reaction_time_accel = random.gauss(mu = 2.5, sigma = 0.0) # 設定成 dt 的話表示不會發呆，設成零可能會有 error
			self.reaction_time_decel = random.gauss(mu = 2.5, sigma = 0.0)

	def compute_save_gap(self):
		self.save_gap = max(2*self.speed, min_gap)
		return self.save_gap
		
class Autonomous_connected_cars(Cars_obj):
	def __init__(self, car_id, is_connected, version = 1):
		super().__init__(car_id)
		if version == 1:
			self.accel = self.max_accel # can modify this value in the future
			self.decel = self.max_decel
			if is_connected == False:
				self.reaction_time_accel = 0.5
				self.reaction_time_decel = 0.5
			else: 
				self.reaction_time_accel = 0.1
				self.reaction_time_decel = 0.1
			
	def compute_save_gap(self, speed_front):
		return 0.1*self.speed + self.speed**2/2.0/self.decel - speed_front**2/2.0/self.decel + min_gap
		# this equation is not all correct
		
# global variable settings
global_version = 2 			
cars_variable_version = 1 	
cars_settings_list = ['human', 'auto', 'auto+is_connected']
cars_settings = cars_settings_list[2]
if cars_settings == 'human':
	is_autonomous = False
	is_connected  = False
elif cars_settings == 'auto':
	is_autonomous = True
	is_connected = False
elif cars_settings == 'auto+is_connected':
	is_autonomous = True
	is_connected = True

min_gap = 5 				# distance between two cars cannot less than min_gap
dt = 0.002
t = 0

if not is_autonomous: max_idle_time = 5 			# 最多發呆五秒
elif not is_connected: max_idle_time = 1
elif is_connected: max_idle_time = 1
initial_mean_speed = 40 	# here! (km/hr)
remove_error_speed = km_to_m(15)
not_jam_speed = km_to_m(20) 
use_speed_color = True 

if global_version == 1:		# default setting
	num_cars = 22 			# at least 2
	circular_radius = 230/2.0/pi 
elif global_version == 2:	# better visiualization setting
	num_cars = 20			# at least 2
	circular_radius = 400/2.0/pi 
	dt = 0.004
elif global_version == 3:   # you can do experiment here
	num_cars = 22 			# at least 2
	circular_radius = 230/2.0/pi 

# For human drivers
if not is_autonomous or True:
	next_action = np.zeros([num_cars, int(max_idle_time/dt)], dtype = np.int8)
	print('next_action =', next_action.shape) 
	# 1 for accel, -1 for decel, 0 for nothing
	# pull in front, and push in the end

# visualization
scene = canvas(background = vec(0.4, 0.7, 0.7), width = 1200, height = 800)
path = cylinder(pos = vec(0, 0, -circular_radius*0.025), axis = vec(0, 0, -circular_radius*0.05), radius = circular_radius * 1.05, color = vec(0.1, 0.2, 0.2))
park = cylinder(pos = vec(0, 0, -circular_radius*0.025+0.1), axis = vec(0, 0, -circular_radius*0.052), radius = circular_radius * 0.95, color = vec(0.4, 0.7, 0.7))
msg = text(text = 'Number of cars = %d\nLength of circular = %d(m)' % (num_cars, circular_radius*2*pi), pos = vec(-18, 0, 0), height = 3) # here!
error_count = 0

cars = []
interval = 2*pi/float(num_cars)
print("interval = %.3f, %.3f" %(interval, interval*circular_radius))
if not is_autonomous:
	for i in range(num_cars): cars.append(Cars_human_driver(i))
else:
	for i in range(num_cars): cars.append(Autonomous_connected_cars(i, is_connected))
	speed_front = [0 for i in range(num_cars)]
	print('reaction time =', cars[1].reaction_time_decel, cars[1].reaction_time_accel)

while True:
	rate(1/dt)
	next_action[:, :-1] = np.copy(next_action[:, 1:]) # update next action array
	
	for i in range(num_cars):
		if is_autonomous:
			if i != 0: speed_front[i] = cars[i-1].speed
			else: speed_front[i] = cars[num_cars-1].speed
			cars[i].save_gap = cars[i].compute_save_gap(speed_front[i])
		else:
			cars[i].save_gap = cars[i].compute_save_gap()
		if i != 0: current_gap = abs(cars[i-1].theta - cars[i].theta)*circular_radius
		else: current_gap = abs(cars[num_cars-1].theta + 2*pi - cars[0].theta)*circular_radius
		
		if current_gap < min_gap: 					# warning 
			#cars[i].speed = 0 						
			cars[i].speed = cars[i].speed * 0.99 	
			if i != 0: cars[i].theta = cars[i-1].theta - to_degree(min_gap)
			else: cars[0].theta = cars[num_cars-1].theta - to_degree(min_gap) + 2*pi
			next_action[i, :] *= 0 					# reset next_action
			cars[i].color = color.white
			error_count += 1
		else:
			if current_gap < cars[i].save_gap: 
				next_action[i][int(cars[i].reaction_time_decel/dt)] = -1
				next_action[i][int(cars[i].reaction_time_decel/dt)+1:] *= 0 		# reset to zero if new action interupt
			else: 
				next_action[i][int(cars[i].reaction_time_accel/dt)] = 1
				next_action[i][int(cars[i].reaction_time_accel/dt)+1:] *= 0
			if next_action[i][0] == 1:    cars[i].speed = cars[i].speed + cars[i].accel*dt
			elif next_action[i][0] == -1: cars[i].speed = cars[i].speed - cars[i].decel*dt
			cars[i].speed = min(cars[i].max_speed, max(cars[i].min_speed, cars[i].speed)) # min_max clip
			cars[i].theta = cars[i].theta + to_degree(cars[i].speed * dt)
			if cars[i].speed > remove_error_speed: cars[i].color = get_color(i, cars[i].speed, use_speed_color)
		cars[i].pos = vec(circular_radius*cos(cars[i].theta), circular_radius*sin(cars[i].theta), 0)
	
	t += 1
	if t % 3000 == 0: 
		output_situation(output_number = min(4, num_cars))
		
