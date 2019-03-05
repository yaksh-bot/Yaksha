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
		'/home/pi/Documents/Yaksha/image_%s.jpg' % dat,				# List files which are to be pushed
		'/home/pi/Documents/Yaksha/thumb_%s.jpg' % dat
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
				"originalContentUrl": "https://yaksh-bot.github.io/Yaksha/image_%s.jpg" % dat,	# Links for Images
				"previewImageUrl": "https://yaksh-bot.github.io/Yaksha/thumb_%s.jpg" % dat       	
			}
		]
	}
	r1 = requests.post( url, headers=head, json=files1 )				# POST request on the url with headers and Message Data
	print "photo sent to mobile"

GPIO.setmode(GPIO.BCM)

# Don't show GPIO pin warnings
GPIO.setwarnings(False)

LED_BULB_PIN = 13

GPIO.setup(LED_BULB_PIN, GPIO.OUT)
GPIO.output(LED_BULB_PIN, True)

try :
	for i in range (0,3) :
		print "starting camera"
		GPIO.output(LED_BULB_PIN, False)
		time.sleep(1)
		camera = PiCamera()									# Define Camera Module Object
		camera.resolution = (640, 480)
		camera.rotation = 270									# rotates camera image 180 degrees 
		image = np.empty((640*480*3), dtype=np.uint8)						# initialize 1-D numpy array of same size as the camera resolution where image would be captured
		camera.capture(image, 'bgr')								# capture image in image array as BGR
		image = image.reshape((480,640,3))							# reshape the original array to 3-D array for further application of that image
		time.sleep(0.5)
		camera.close()
		GPIO.output(LED_BULB_PIN, True)										# Close camera Module
		dat = time.strftime("%d-%m-%Y_%H:%M:%S")
		cv2.imwrite('/home/pi/Documents/Yaksha/image_%s.jpg' % dat, image)				# save image
		thumbnail = cv2.resize(image, (133, 100))
		cv2.imwrite('/home/pi/Documents/Yaksha/thumb_%s.jpg' % dat, thumbnail)
		git_push(dat)											# push to git
		send_to_phone(dat, "Test Camera light")								# send to mobile
		time.sleep(1)
except KeyboardInterrupt:
	GPIO.cleanup()