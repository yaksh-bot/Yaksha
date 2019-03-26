from picamera import PiCamera
import time, datetime
import cv2
import os, re
import requests
import RPi.GPIO as GPIO
from git import Repo
import threading
import numpy as np


def git_push(dat) :

	"""This function push image to the git"""

	repo_dir = '.'											# Define repo_dir which is same as the file directory
	repo = Repo(repo_dir)									# Create Repo object with the repo directory
	file_list = [												
		os.path.join(os.getcwd(),'image_%s.jpg' % dat),				# List files which are to be pushed
		os.path.join(os.getcwd(),'thumb_%s.jpg' % dat)
	]
	commit_message = 'push image_%s' % dat							# commit message	
	repo.index.add(file_list)								# add files 
	repo.index.commit(message=commit_message)				# add commit message
	origin = repo.remote('origin')							# Define orgin branch where the file has to be pushed
	origin.push(repo.head)									# Push the file	
	print "photo pushed to git" 


def send_image(dat) :

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
				"type": "image",
				"originalContentUrl": "https://yaksh-bot.github.io/Yaksha/image_%s.jpg" % dat,	# Links for Images
				"previewImageUrl": "https://yaksh-bot.github.io/Yaksha/thumb_%s.jpg" % dat       	
			}
		]
	}
	r1 = requests.post( url, headers=head, json=files1 )				# POST request on the url with headers and Message Data
	print "photo sent to mobile"


def send_message(message) :

	"""
		This function sends message to mobile via Line Messanger
	"""

	url = 'https://api.line.me/v2/bot/message/push'					# API endpoint for sending message

	head = {"Authorization": "Bearer  Pu69VmOjkFMP3gQgFBnL/whGQhMxsXLoe/z8+S7PNw9x8fTsBgdlC5MSPoVlqezEU3HHLfcnyaZCd1w69vraUB9rp6kUkXkz9wj9rXQ1+6elkvGLjvQVR2eZ7MF1/KS4mblhpsGO7Om9VT/Fpe2GngdB04t89/1O/w1cDnyilFU=", "Content-Type": "application/json"}											# Authorization token and content type defination

	files1 = {	
		"to": "U3b241ca9a1532afbb9af5f98a549dc9c",				# Receiver ID
		"messages":[								# Message which has to be sent
			{		
				"type": "text",
				"text": message
			}
		]
	}
	r1 = requests.post( url, headers=head, json=files1 )				# POST request on the url with headers and Message Data


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
				"originalContentUrl": "https://yaksh-bot.github.io/Yaksha/image_%s.jpg" % dat,	# Links for Images
				"previewImageUrl": "https://yaksh-bot.github.io/Yaksha/thumb_%s.jpg" % dat       	
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
	
	while cam_var != 0 :										# Wait till camera resource is not empty
		time.sleep(0.1)

	cam_var = 1													# Set cam_var to 1 so that no other thread is able to use camera Module (Else an error occurs) 
	camera = PiCamera()											# Define Camera Module Object
	camera.resolution = (640, 480)								# set image resolution 
	camera.rotation = 270										# rotates camera image 270 degrees 
														
	image = np.empty((640*480*3), dtype=np.uint8)				# initialize 1-D numpy array of same size as the camera resolution where image would be captured
	camera.capture(image, 'bgr')								# capture image in image array as BGR
	image = image.reshape((480,640,3))							# reshape the original array to 3-D array for further application of that image
	camera.close()												# Close camera Module
	
	cam_var = 0													# Set cam_var to 0 so that other threads can now use the camera 
	time_face = datetime.datetime.now()							# set time_face as current time 
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)					# convert RGB image into grayscale image	
	faces = face_cascade.detectMultiScale(gray, 1.3, 5)				# detect faces in the image
	return faces, image


def face_detected(faces, image, dat):

	"""
	This function marks face on the image and sends image to mobile
	"""
	print "faces detected"
	for (x,y,w,h) in faces:
		cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),1)						# Draw rectangle around face
	cv2.imwrite(os.path.join(os.getcwd(),'image_%s.jpg' % dat), image)				# save image

	thumbnail = cv2.resize(image, (133, 100))
	cv2.imwrite(os.path.join(os.getcwd(),'thumb_%s.jpg' % dat), thumbnail)

	git_push(dat)															# push to git
	send_to_phone(dat, "I could detect a Face!!")									# send message to line					


def take_photo_door():

	"""
	This function is called when door magnet sensor is activated.
	It Synchronizes events frequency based on time elapsed and send the captured images to mobile.
	"""
	global time_door, start_door, cam_var, time_face, start_door_photo, last_face, first_face
	
	if start_door == 0:													# If the door has opened for the first time	
		print "Entered"
		start_door = 1												
		start_door_photo = 1
		send_message("Someone opened your Locker!!")					# Send Message

	if (datetime.datetime.now() - time_face).seconds >= 1:	

		faces, image = capture()												# Capture a photo
		dat = time.strftime("%d-%m-%Y_%H:%M:%S")

		if len(faces) > 0 and ((datetime.datetime.now() - last_face).seconds >= 5 or first_face == 0) :  # check if faces are detected and time between last sent photo is more than 5 seconds
			last_face = datetime.datetime.now()
			first_face = 1
			face_detected(faces, image, dat)			

		elif (datetime.datetime.now() - time_door).seconds >= 5 or start_door_photo == 1:
			print "taking photo!!"
			start_door_photo = 0
			cv2.imwrite(os.path.join(os.getcwd(),'image_%s.jpg' % dat), image)			# Save image	
			thumbnail = cv2.resize(image, (133, 100))
			cv2.imwrite(os.path.join(os.getcwd(),'thumb_%s.jpg' % dat), thumbnail)		# Save thumbnail
			print "A photo has been captured!!"
			time_door = datetime.datetime.now()								# Save current time in time_door so that counter starts again
			git_push(dat)													# Push to git
			send_image(dat)													# Send image to phone


def take_photo_motion(last_motion):

	"""
	This function is called when Motion sensor is activated.
	It Synchronizes events frequency based on time elapsed and send the captured images to mobile.
	"""

	global time_motion, cam_var, time_face, photo_motion, last_face, first_face
	
	if (datetime.datetime.now() - time_face).seconds >= 1:

		if (datetime.datetime.now() - time_motion).seconds >= 2 or last_motion == 0:
			send_message("Someone is around your Locker!!")	
			time_motion = datetime.datetime.now()										# Save current time in time_motion so that counter starts again

		faces, image = capture()														# Capture image
		dat = time.strftime("%d-%m-%Y_%H:%M:%S")

		if len(faces) > 0 and ((datetime.datetime.now() - last_face).seconds >= 5 or first_face == 0):	# check if faces are detected and time between last sent photo (face detected) is more than 5 seconds
			first_face = 1
			last_face = datetime.datetime.now()
			face_detected(faces, image, dat)

		elif (datetime.datetime.now() - photo_motion).seconds >= 10:						
			print "taking photo!!"
			cv2.imwrite(os.path.join(os.getcwd(),'image_%s.jpg' % dat), image)				# Save image
			thumbnail = cv2.resize(image, (133, 100))										
			cv2.imwrite(os.path.join(os.getcwd(),'thumb_%s.jpg' % dat), thumbnail)			# Save image thumbnail	
			print "A photo has been captured!!"
			photo_motion = datetime.datetime.now()
			git_push(dat)																# Push to git			
			send_image(dat)																# Send image to phone


def delete_old_images() :

	"""
	Function to delete all images from the folder before today's date
	"""
	# iterate over every file in the folder
	for i in os.listdir(os.getcwd()):

		if re.search('image*', i) or re.search('thumb*', i) :							# Seach if file name starts with 'image' or 'thumb'
			file_created_date = datetime.datetime.fromtimestamp(os.path.getctime(i)).date()		
			today_date = datetime.datetime.now().date()											

			if file_created_date != today_date :										# if both dates are not same 
				os.remove(os.path.join(os.getcwd(), i))									# Delete the file

	print "old images deleted"
	
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
		take_photo_door()


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
		take_photo_motion(self.last_motion)


class FilesDeleteThread (threading.Thread):

	"""
	Thread Class used for deleting image files older than today
	"""

	def __init__(self):
		"""
		Initialization of thread class
		"""
		threading.Thread.__init__(self)

	def run(self):
		"""
		Functions to be performed in the thread are listed here
		"""
		delete_old_images()


"""
********************************************************Main Program Starts Here************************************
"""

files_thread = FilesDeleteThread()
files_thread.start()

time_door = datetime.datetime.now()
time_motion = datetime.datetime.now()
time_face = datetime.datetime.now()
time_activity = datetime.datetime.now()
photo_motion = datetime.datetime.now()
last_face = datetime.datetime.now()

# Set Broadcom mode so we can address GPIO pins by number.
GPIO.setmode(GPIO.BCM)

# Don't show GPIO pin warnings
GPIO.setwarnings(False)

# These are the GPIO pin numbers we are using
DOOR_SENSOR_PIN = 4
DOOR_LED_PIN = 10
MOTION_SENSOR_PIN = 14
MOTION_LED_PIN = 21
LED_BULB_PIN = 13
APP_LED_PIN = 7

GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)				# Set up the door sensor pin

GPIO.setup(MOTION_SENSOR_PIN, GPIO.IN)										# Set up the Motion Sensor pin

GPIO.setup(DOOR_LED_PIN, GPIO.OUT)									# Set up the door sensor LED pin
GPIO.output(DOOR_LED_PIN, False)									# Initialize it to False so it doesnot glow

GPIO.setup(MOTION_LED_PIN, GPIO.OUT)								# Set up the Motion Sensor LED pin
GPIO.output(MOTION_LED_PIN, False)									# Initialize it to False so it doesnot glow

GPIO.setup(LED_BULB_PIN, GPIO.OUT)
GPIO.output(LED_BULB_PIN, True)

GPIO.setup(APP_LED_PIN, GPIO.OUT)
GPIO.output(APP_LED_PIN, False)

# Define Face detection classifier from the xml file
face_cascade = cv2.CascadeClassifier(os.path.join(os.getcwd(),'haarcascade_frontalface_default.xml')) 

thread_no = 0											# Thread number 
start_door = 0											# Variable to mark if door has just been opened for sending the message 
cam_var = 0												# Variable to ensure 
last_motion = 0
prev_door_inp = 0
start_door_photo = 0									# Variable to mark if door has just been opened for clicking a photo
first_face = 0

GPIO.output(APP_LED_PIN, True)

try :
	while True :
		if (datetime.datetime.now() - time_activity).seconds > 10:
			GPIO.output(LED_BULB_PIN, True)										# Turn off led light
		
		door_input = GPIO.input(DOOR_SENSOR_PIN)								# door magnet sensor input
		motion_input = GPIO.input(MOTION_SENSOR_PIN)							# motion sensor input

		if motion_input == 1 and door_input == 1 :			
			GPIO.output(DOOR_LED_PIN, True)
			GPIO.output(MOTION_LED_PIN, True)
			GPIO.output(LED_BULB_PIN, False)
			time_activity = datetime.datetime.now()
			door_thread = DoorThread(thread_no, "Thread-%s" % thread_no, thread_no)
			thread_no += 1
			door_thread.start()		

		elif motion_input == 1 and door_input == 0 :
			GPIO.output(DOOR_LED_PIN, False)
			GPIO.output(MOTION_LED_PIN, True)
			GPIO.output(LED_BULB_PIN, False)
			time_activity = datetime.datetime.now()
			motion_thread = MotionThread(thread_no, "Thread-%s" % thread_no, thread_no, last_motion)
			thread_no += 1
			motion_thread.start()
			time_door = datetime.datetime.now()
			start_door = 0		
			start_door_photo = 0

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
			start_door_photo = 0

		if prev_door_inp == 1 and door_input == 0:							# If door is closed
			print "closed"
			send_message("Locker is now closed!!")							# Send Message
			
		last_motion = motion_input
		prev_door_inp = door_input	
		time.sleep(0.5)

except KeyboardInterrupt:
	GPIO.cleanup()