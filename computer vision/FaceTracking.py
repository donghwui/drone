import cv2
import numpy as np
from djitellopy import tello
import time

# init and connect to drone
drone = tello.Tello()
drone.connect()
print(drone.get_battery())
drone.streamon()

drone.takeoff()

# move up the drone
drone.send_rc_control(0, 0, 25, 0)
time.sleep(2.2)

# window width and height
w, h = 360, 240

# fwd/bwd range for the drone to maintain distance from the face
fbRange = [6200, 6800]

# PID (Proportional, Integral, Derivative) constants
pid = [0.4, 0.4, 0]
pError = 0  # Previous error for the PID controller


def findFace(img):
    # Load the Haar Cascade for face detection
    faceCascade = cv2.CascadeClassifier("resources/haarcascades/haarcascade_frontalface_default.xml")
    # Convert the image to grayscale
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces in the image in [x, y, w, h] where (x, y): top-left corner of the rectangle, w: width, h: height
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListC = []  # store center coordinates of detected faces
    myFaceListArea = []  # store area of detected faces

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Draw a rectangle around the detected face
        # calculate the center of the face in (x, y)
        cx = x + w // 2
        cy = y + h // 2
        # calculate the area of the face
        area = w * h
        # draw a circle at the center of the face
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        # append the center and area of the face
        myFaceListC.append([cx, cy])
        myFaceListArea.append(area)

    if len(myFaceListArea) != 0:
        # index of the area with the largest face
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListC[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]


# Function to track the face and control the drone
def trackFace(info, w, pid, pError):
    area = info[1]  # area of the face
    x, y = info[0]  # coordinates of the face
    fb = 0  # init the fwd/bwd movement variable
    error = x - w // 2  # Calculate the error in the x-coordinate
    # where x: x coord of center of the detected face
    # w // 2: x coord of center of the image frame
    speed = pid[0] * error + pid[1] * (error - pError)  # Calculate the speed using PID controller
    speed = int(np.clip(speed, -100, 100))  # Clip the speed to be within the range [-100, 100]

    if fbRange[0] < area and area < fbRange[1]:
        fb = 0  # no need to move as it is within the range
    elif area > fbRange[1]:
        fb = -20  # face area is too large -> drone is too close -> move backward
    elif area < fbRange[0] and area != 0:
        fb = 20  # face area is too small -> drone is too far -> move forward

    # no face detected -> no rotation
    if x == 0:
        speed = 0
        error = 0

    # Send the control command to the drone
    drone.send_rc_control(0, fb, 0, speed)
    return error  # Return the current error


while True:
    img = drone.get_frame_read().frame  # Get the current frame from the drone's video stream
    img = cv2.resize(img, (w, h))  # Resize the frame for display and faster processing
    img, info = findFace(img)  # Find the face in the frame
    pError = trackFace(info, w, pid, pError)  # Track the face and control the drone

    cv2.imshow("Output", img)  # Display the frame
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Break the loop if 'q' key is pressed
        drone.land()  # Land the drone
        break  # Exit the loop
