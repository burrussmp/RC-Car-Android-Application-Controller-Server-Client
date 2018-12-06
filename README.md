# RC Car Android Application
Deliverables
A RC car that can be controlled by an Android Application.
The RC car is controlled by a Raspberry Pi 3 which collects images from a USB webcam
The Raspberry Pi 3 sends images to the client application which displays the live feed in a window
The client sends controls (acceleration and steering duty cycles) to the Raspberry Pi 3 which is used to control the GPIO pins that ultimately control the steering servos and the acceleration motor.
The application has a password protected text field. Only clients with the appropriate VIEW password can view the images collected by the Raspberry Pi 3 and only clients with the appropriate CONTROL password can control the RC Car.
The application has a third text field that controls what type of image is sent to the application. The configurations supported are CARTOON mode, LANE DETECTION mode, and normal mode i.e. unfiltered images.
The client/server communication paradigm uses UDP/IP.
The client and the server are multi-threaded applications
