# RC Car Android Application
## Authors
Matthew Burruss and Gaby Gallego
## Project Features
RCServer2.py => Server that is meant to run on the Raspberry Pi 3. Before running the script, ensure IO.py is in the same directly and run sudo pigpiod to initialize the pigpio daemon.

RCClient2.py => Able to run on any client computer to control the car. Uses the cursor location to control the RC car.

Android Application => Can be installed on any Android device. See PPT for full features. The Android app allows a user to control the car with 2 sliding bars. Furthermore, the app has an ImageView that shows a livestream from the RC Car's USB camera.
## Hardware Architecture
The project uses the Traxxas RC Slash RC car as the framework. A raspberry pi 3 controls the RC car's steering servos and acceleration  motor using pulse width modulation (PWM) generated on two of its GPIO pins (19 and 18). The raspberry pi is also connected to a USB camera.
## Software Architecture
A UDP server/client paradigm is created with a mulit-threaded data and camera thread on both the client and the server. OpenCV open source is used to configure and control the camera as well as to perform image processing on the image.
## Cool features
- The viewer and the controller are password protected. The client must send the appropriate passwords to control and view. See the ppt for more details or the listed client code.

- Lane detection can be enabled by typing in DETECT LANE in the text field of the android app or by changing RCClient.py 

- Cartoon mode by typing CARTOON in the text field or changing the RCClient.py
## Deliverables
- A RC car that can be controlled by an Android Application.

The RC car is controlled by a Raspberry Pi 3 which collects images from a USB webcam

The Raspberry Pi 3 sends images to the client application which displays the live feed in a window

The client sends controls (acceleration and steering duty cycles) to the Raspberry Pi 3 which is used to control the GPIO pins that ultimately control the steering servos and the acceleration motor.

The application has a password protected text field. Only clients with the appropriate VIEW password can view the images collected by the Raspberry Pi 3 and only clients with the appropriate CONTROL password can control the RC Car.

The application has a third text field that controls what type of image is sent to the application. The configurations supported are CARTOON mode, LANE DETECTION mode, and normal mode i.e. unfiltered images.

The client/server communication paradigm uses UDP/IP.

The client and the server are multi-threaded applications.
