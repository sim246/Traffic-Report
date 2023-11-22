from picamera2 import Picamera2, Preview
import time

def take_picture(detection):
	picam2 = Picamera2()
	camera_config = picam2.create_preview_configuration()
	picam2.configure(camera_config)
	
	if (detection == true):
		picam2.start_preview(Preview.QT)
		picam2.start()
		time.sleep(5)
		picam2.capture_file("car_capture.jpg")
		return true
	else:
		return false

