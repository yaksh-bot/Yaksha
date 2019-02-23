from picamera import PiCamera
import time
import datetime
import cv2
import requests
import RPi.GPIO as GPIO
from git import Repo
import threading
import numpy as np


def git_push (dat) :

	"""This function push image to the git"""

	repo_dir = '.'										# Define repo_dir which is same as the file directory
	repo = Repo(repo_dir)									# Create Repo object with the repo directory
	file_list = [												
		'/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat,				# List files which are to b pushed
		'/home/pi/Documents/Raspberrypi/thumb_%s.jpg' % dat
	]
	commit_message = 'push image_%s' % dat							# commit message	
	repo.index.add(file_list)								# add files 
	repo.index.commit(message=commit_message)						# add commit message
	origin = repo.remote('origin')								# Define orgin branch where the file has to be pushed
	origin.push(repo.head)									# Push the file	
	print "photo pushed to git" 


def send_to_phone(dat, message) :

	"""
		This function sends image saved 
		on github to mobile via Line Messanger
	"""

	url = 'https://api.line.me/v2/bot/message/push'					# API endpoint for sending message

	head = {"Authorization": "Bearer  Pu69VmOjkFMP3gQgFBnL/whGQhMxsXLoe/z8+S7PNw9x8fTsBgdlC5MSPoVlqezEU3HHLfcnyaZCd1w69vraUB9rp6kUkXkz9wj9rXQ1+6elkvGLjvQVR2eZ7MF1/KS4mblhpsGO7Om9VT/Fpe2GngdB04t89/1O/w1cDnyilFU=", "Content-Type": "application/json"}											# Authorization token and content type defination

	files1 = {	
		"to": "U3b241ca9a1532afbb9af5f98a549dc9c",				# Receiver ID
		"messages":[								# Message which has to be sent
			{		
				"type": "text",
				"text": message
			},
			{
				"type": "image",
				"originalContentUrl": "https://namanjain10.github.io/Raspberrypi/image_%s.jpg" % dat,	# Links for Images
				"previewImageUrl": "https://namanjain10.github.io/Raspberrypi/thumb_%s.jpg" % dat       	
			}
		]
	}
	r1 = requests.post( url, headers=head, json=files1 )				# POST request on the url with headers and Message Data
	print "photo sent to mobile"


def capture() :

	"""
	This function Captures and returns image and saves it to numpy array 
	and detects and returns faces in that image
	"""

	global cam_var, time_face, face_cascade
	print "starting camera"

	camera = PiCamera()									# Define Camera Module Object
	camera.resolution = (640, 480)
	# camera.rotation = 180									# rotates camera image 180 degrees 
	cam_var = 1										# Set cam_var to 1 so that no other thread is able to use camera Module (Else an error occurs) 
	image = np.empty((640*480*3), dtype=np.uint8)						# initialize 1-D numpy array of same size as the camera resolution where image would be captured
	camera.capture(image, 'bgr')								# capture image in image array as BGR
	image = image.reshape((640,480,3))							# reshape the original array to 3-D array for further application of that image
	camera.close()										# Close camera Module
	time_face = datetime.datetime.now()							# set time_face as current time 
	cam_var = 0										# Set cam_var to 0 so that other threads can now use the camera 
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)						# convert RGB image into grayscale image	
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)					# detect faces in the image
	return faces, image


def face_detected(faces, image, dat):

	"""
	This function marks face on the image and sends image to mobile
	"""

	print "faces detected"
	for (x,y,w,h) in faces:
		cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),1)					# Draw rectangle around face	
	cv2.imwrite('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat, image)				# save image
	thumbnail = image.reshape((20, 20))
	cv2.imwrite('/home/pi/Documents/Raspberrypi/thumb_%s.jpg' % dat, thumbnail)
	git_push(dat)											# push to git
	send_to_phone(dat, "Face Detected")								# send to mobile


def take_photo_door():

	"""
	This function is called when door magnet sensor is activated.
	It Synchronizes events frequency based on time elapsed and send the captured images to mobile.
	"""

	global time_door, start_door, cam_var, time_face
	
	if (datetime.datetime.now() - time_face).seconds > 1  and cam_var == 0 :		
		faces, image = capture()
		dat = str(datetime.datetime.now())

		if len(faces) > 0 :
			face_detected(faces, image, dat)

		elif (datetime.datetime.now() - time_door).seconds >= 10 or start_door == 0:
			print "taking photo!!"
			start_door = 1
			dat = datetime.datetime.now().strftime('%s')
			cv2.imwrite('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat, image)
			thumbnail = image.reshape((20, 20))
			cv2.imwrite('/home/pi/Documents/Raspberrypi/thumb_%s.jpg' % dat, thumbnail)
			print "A photo has been captured!!"
			time_door = datetime.datetime.now()							# Save current time in time_door so that counter starts again
			git_push(dat)										# Push to git
			send_to_phone(dat, "Sent from RaspberryPi")						# Send image to phone


def take_photo_motion(last_motion):

	"""
	This function is called when Motion sensor is activated.
	It Synchronizes events frequency based on time elapsed and send the captured images to mobile.
	"""

	global time_motion, cam_var, time_face
	
	if (datetime.datetime.now() - time_face).seconds > 1  and cam_var == 0 :		
		faces, image = capture()
		dat = str(datetime.datetime.now())

		if len(faces) > 0 :
			face_detected(faces, image, dat)

		elif (datetime.datetime.now() - time_motion).seconds > 2 or last_motion == 0:
			print "taking photo!!"
			cv2.imwrite('/home/pi/Documents/Raspberrypi/image_%s.jpg' % dat, image)			# Save image
			thumbnail = image.reshape((20, 20))
			cv2.imwrite('/home/pi/Documents/Raspberrypi/thumb_%s.jpg' % dat, thumbnail)
			print "A photo has been captured!!"
			time_motion = datetime.datetime.now()							# Save current time in time_motion so that counter starts again 
			git_push(dat)										# Push to git
			send_to_phone(dat, "Sent from RaspberryPi")						# Send image to phone


class DoorThread (threading.Thread):

	"""
	Thread Class used for creating seperate threads when door magnet sensor is activated
	takes 3 params at init (no time) - 
	properties: thread_id, name, counter  
	"""

	def __init__(self, threadID, name, counter):
		"""
		Initialization of thread class
		"""
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

	def run(self):
		"""
		Functions to be performed in the thread are listed here
		"""
		# print "Starting " + self.name
		take_photo_door()
		# print "Exiting " + self.name


class MotionThread (threading.Thread):

	"""
	Thread Class used for creating seperate threads when Motion sensor is activated
	takes 4 params at init (no time) - 
	properties: thread_id, name, counter, last_motion (last motion sensor output)  
	"""

	def __init__(self, threadID, name, counter, last_motion):
		"""
		Initialization of thread class
		"""
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter
		self.last_motion = last_motion

	def run(self):
		"""
		Functions to be performed in the thread are listed here
		"""
		# print "Starting " + self.name
		take_photo_motion(self.last_motion)
		# print "Exiting " + self.name


# Set Broadcom mode so we can address GPIO pins by number.
GPIO.setmode(GPIO.BCM)

# Don't show GPIO pin warnings
GPIO.setwarnings(False)

# These are the GPIO pin numbers we are using
DOOR_SENSOR_PIN = 4
DOOR_LED_PIN = 10
MOTION_SENSOR_PIN = 14
MOTION_LED_PIN = 21


GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)					# Set up the door sensor pin

GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)								# Set up the Motion Sensor pin

GPIO.setup(DOOR_LED_PIN, GPIO.OUT)								# Set up the door sensor LED pin
GPIO.output(DOOR_LED_PIN, False)								# Initialize it to False so it doesnot glow

GPIO.setup(MOTION_LED_PIN, GPIO.OUT)								# Set up the Motion Sensor LED pin
GPIO.output(MOTION_LED_PIN, False)								# Initialize it to False so it doesnot glow


# Define Face detection classifier from the xml file
face_cascade = cv2.CascadeClassifier('/home/pi/Documents/haarcascade_frontalface_default.xml') 

thread_no = 0											# Thread number 
start_door = 0											# Variable to mark if door has just been open
cam_var = 0											# Variable to ensure 

time_door = datetime.datetime.now()
time_motion = datetime.datetime.now()
time_face = datetime.datetime.now()
last_motion = 0

try :
	while True :
		door_input = inp = GPIO.input(DOOR_SENSOR_PIN)							# door magnet sensor
		motion_input = GPIO.input(MOTION_SENSOR_PIN)							# motion sensor

		if motion_input == 1 and door_input == 1 :
			GPIO.output(DOOR_LED_PIN, True)
			GPIO.output(MOTION_LED_PIN, True)
			door_thread = DoorThread(thread_no, "Thread-%s" % thread_no, thread_no)
			thread_no += 1
			door_thread.start()		

		elif motion_input == 1 and door_input == 0 :
			GPIO.output(DOOR_LED_PIN, False)
			GPIO.output(MOTION_LED_PIN, True)
			motion_thread = MotionThread(thread_no, "Thread-%s" % thread_no, thread_no, last_motion)
			thread_no += 1
			motion_thread.start()
			time_door = datetime.datetime.now()
			start_door = 0		

		elif motion_input == 0 and door_input == 1 :
			GPIO.output(MOTION_LED_PIN, False)
			GPIO.output(DOOR_LED_PIN, True)
			door_thread = DoorThread(thread_no, "Thread-%s" % thread_no, thread_no)
			thread_no += 1
			door_thread.start()		
			time_motion = datetime.datetime.now()

		else :
			GPIO.output(MOTION_LED_PIN, False)
			GPIO.output(DOOR_LED_PIN, False)
			time_motion = datetime.datetime.now()
			time_door = datetime.datetime.now()
			start_door = 0

		last_motion = motion_input	
		time.sleep(0.3)

except KeyboardInterrupt:
	GPIO.cleanup()