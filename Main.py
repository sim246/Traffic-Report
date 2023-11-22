from picamera2 import Picamera2, Preview
import time
from random import randrange

def take_picture(detection_type, detection_color, detection):
	if (detection == True and detection_type == "motion" and detection_color == "red"):
		picam2 = Picamera2()
		camera_config = picam2.create_preview_configuration()
		picam2.configure(camera_config)
		picam2.start_preview(Preview.QT)
		picam2.start()
		time.sleep(5)
		picam2.capture_file("car_capture_motion.jpg")
		return True
	elif (detection == True and detection_type == "colision"):
		picam2 = Picamera2()
		camera_config = picam2.create_preview_configuration()
		picam2.configure(camera_config)
		picam2.start_preview(Preview.QT)
		picam2.start()
		time.sleep(5)
		picam2.capture_file("car_capture_colision.jpg")
		return True
	else:
		return False

def random_color():
	intcolor = randrange(3)
	if (intcolor == 0):
		print("red")
		return "red"
	if (intcolor == 1):
		print("blue")
		return "blue"
	if (intcolor == 2):
		print("green")
		return "green"

if __name__ == '__main__':
	color = random_color()
	take_picture("colision", color, True)
