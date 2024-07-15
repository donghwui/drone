from djitellopy import tello
import KeyPressModule as kp
import numpy as np
from time import sleep
import cv2
import math

######## PARAMETERS ###########
fSpeed = 117 / 10  # Forward Speed in cm/s (11.7cm/s)
aSpeed = 360 / 10  # Angular Speed Degrees/s (36°/s)
interval = 0.25    # Time interval for control loop
dInterval = fSpeed * interval  # Distance interval per control loop
aInterval = aSpeed * interval  # Angular interval per control loop
###############################################

x, y = 500, 500  # Starting coordinates (center of a 1000x1000 image)
a = 0            # Initial angle
yaw = 0          # Initial yaw angle

kp.init()  # Initialize the key press module

me = tello.Tello()  # Create an instance of the Tello drone
me.connect()  # Connect to the Tello drone

print(me.get_battery())  # Print the current battery level of the drone

points = [(0, 0), (0, 0)]  # List to store points for drawing the drone's path
# input: keyboard commands
# output: updated [lr, fb, ud, yv, x, y]
def getKeyboardInput():
    # init left-right (lr), forward-backward (fb), up-down (ud), and yaw (yv) movements
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 15   # Speed for linear movements
    aspeed = 50  # Speed for angular movements

    global x, y, yaw, a
    d = 0  # Distance moved in current interval

    if kp.getKey("LEFT"):
        lr = -speed  # Move left
        d = dInterval
        a = -180
    elif kp.getKey("RIGHT"):
        lr = speed  # Move right
        d = -dInterval
        a = 180
    if kp.getKey("UP"):
        fb = speed  # Move forward
        d = dInterval
        a = 270
    elif kp.getKey("DOWN"):
        fb = -speed  # Move backward
        d = -dInterval
        a = -90
    if kp.getKey("w"):
        ud = speed  # Move up
    elif kp.getKey("s"):
        ud = -speed  # Move down
    if kp.getKey("a"):
        yv = -aspeed  # Yaw left
        yaw -= aInterval
    elif kp.getKey("d"):
        yv = aspeed  # Yaw right
        yaw += aInterval

    if kp.getKey("q"):
        me.land()  # Land the drone
        sleep(3)  # Pause for 3 seconds
    if kp.getKey("e"):
        me.takeoff()  # Takeoff the drone

    sleep(interval)  # Pause for the specified interval

    # use trig to update angle and position
    a += yaw
    x += int(d * math.cos(math.radians(a)))
    y += int(d * math.sin(math.radians(a)))

    return [lr, fb, ud, yv, x, y]

def drawPoints(img, points):
    # Draw circles at each point in the points list
    for point in points:
        cv2.circle(img, point, 5, (0, 0, 255), cv2.FILLED)

    # Draw a green circle at the last point (current position)
    cv2.circle(img, points[-1], 8, (0, 255, 0), cv2.FILLED)

    # Display the coordinates of the current position
    cv2.putText(img, f'({(points[-1][0] - 500) / 100},{(points[-1][1] - 500) / 100})m',
                (points[-1][0] + 10, points[-1][1] + 30), cv2.FONT_HERSHEY_PLAIN, 1,
                (255, 0, 255), 1)

while True:
    vals = getKeyboardInput()
    me.send_rc_control(vals[0], vals[1], vals[2], vals[3])

    img = np.zeros((1000, 1000, 3), np.uint8)  # Create a black image for drawing the path

    # Check if the position has changed and update the points list
    if points[-1][0] != vals[4] or points[-1][1] != vals[5]:
        points.append((vals[4], vals[5]))

    # Draw the path on the image
    drawPoints(img, points)

    cv2.imshow("Output", img)  # Display the image
    cv2.waitKey(1)  # Wait for 1ms to allow the window to refresh
