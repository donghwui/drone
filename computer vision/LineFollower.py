import numpy as np
from djitellopy import tello
import cv2

# init and connect to drone
drone = tello.Tello()
drone.connect()
print(drone.get_battery())
drone.streamon()
# drone.takeoff()  # Uncomment this line to take off the drone

cap = cv2.VideoCapture(1)

# HSV color range values for thresholding
hsvVals = [0, 0, 188, 179, 33, 245]

# Number of sensors
sensors = 3
# Threshold for detecting an object
threshold = 0.2

# Width and height of the image
width, height = 480, 360

# Sensitivity for left-right movement
senstivity = 3  # Higher value means less sensitive

# Weights for different sensor outputs
weights = [-25, -15, 0, 15, 25]

# Forward speed
fSpeed = 15

# Curve value for rotation
curve = 0

# Function to threshold the image based on HSV values
def thresholding(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convert the image to HSV color space
    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])  # Lower HSV bound
    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])  # Upper HSV bound
    mask = cv2.inRange(hsv, lower, upper)  # Create a mask based on the HSV range
    return mask

# Function to find contours in the thresholded image
def getContours(imgThres, img):
    cx = 0  # Initialize the x-coordinate of the contour's center
    contours, hieracrhy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)  # Find contours

    if len(contours) != 0:
        biggest = max(contours, key=cv2.contourArea)  # Find the biggest contour
        x, y, w, h = cv2.boundingRect(biggest)  # Get the bounding rectangle of the biggest contour
        cx = x + w // 2  # Calculate the x-coordinate of the center
        cy = y + h // 2  # Calculate the y-coordinate of the center
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)  # Draw the biggest contour
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)  # Draw a circle at the center

    return cx

# Function to get sensor output based on the thresholded image
def getSensorOutput(imgThres, sensors):
    imgs = np.hsplit(imgThres, sensors)  # Split the image into equal parts based on the number of sensors
    totalPixels = (imgThres.shape[1] // sensors) * imgThres.shape[0]  # Calculate total pixels in each sensor part
    senOut = []

    for x, im in enumerate(imgs):
        pixelCount = cv2.countNonZero(im)  # Count non-zero pixels in each part
        if pixelCount > threshold * totalPixels:
            senOut.append(1)  # Sensor is active
        else:
            senOut.append(0)  # Sensor is inactive

    return senOut

# Function to send commands to the drone based on sensor output and contour center
def sendCommands(senOut, cx):
    global curve

    # Calculate left-right movement
    lr = (cx - width // 2) // senstivity
    lr = int(np.clip(lr, -10, 10))
    if 2 > lr > -2: lr = 0

    # Calculate rotation based on sensor output
    if   senOut == [1, 0, 0]: curve = weights[0]
    elif senOut == [1, 1, 0]: curve = weights[1]
    elif senOut == [0, 1, 0]: curve = weights[2]
    elif senOut == [0, 1, 1]: curve = weights[3]
    elif senOut == [0, 0, 1]: curve = weights[4]
    elif senOut == [0, 0, 0]: curve = weights[2]
    elif senOut == [1, 1, 1]: curve = weights[2]
    elif senOut == [1, 0, 1]: curve = weights[2]

    drone.send_rc_control(lr, fSpeed, 0, curve)  # Send control commands to the drone

while True:
    # img = cap.read()  # Capture frame from external camera (commented out as drone camera is used)
    img = drone.get_frame_read().frame  # Get the current frame from the drone's video stream
    img = cv2.resize(img, (width, height))  # Resize the frame
    img = cv2.flip(img, 0)  # Flip the frame vertically

    imgThres = thresholding(img)  # Apply thresholding
    cx = getContours(imgThres, img)  # Get the contour's center
    senOut = getSensorOutput(imgThres, sensors)  # Get sensor output

    sendCommands(senOut, cx)  # Send commands to the drone

    cv2.imshow("Output", img)  # Display the original frame
    cv2.imshow("Path", imgThres)  # Display the thresholded frame
    cv2.waitKey(1)  # Wait for 1 ms before moving to the next frame

# Color Picker

from djitellopy import tello
import cv2
import numpy as np

frameWidth = 480  # Frame width
frameHeight = 360  # Frame height

drone = tello.Tello()
drone.connect()
print(drone.get_battery())  # Print the current battery level of the drone
drone.streamon()  # Start the video stream from the drone's camera

# Function to create an empty callback
def empty(a):
    pass

# Create a window named "HSV" for trackbars
cv2.namedWindow("HSV")
cv2.resizeWindow("HSV", 640, 240)  # Resize the window

# Create trackbars for adjusting HSV values
cv2.createTrackbar("HUE Min", "HSV", 0, 179, empty)
cv2.createTrackbar("HUE Max", "HSV", 179, 179, empty)
cv2.createTrackbar("SAT Min", "HSV", 0, 255, empty)
cv2.createTrackbar("SAT Max", "HSV", 255, 255, empty)
cv2.createTrackbar("VALUE Min", "HSV", 0, 255, empty)
cv2.createTrackbar("VALUE Max", "HSV", 255, 255, empty)

# cap = cv2.VideoCapture(1)  # Initialize video capture from an external camera (commented out as drone camera is used)

frameCounter = 0  # Initialize frame counter

while True:
    img = drone.get_frame_read().frame  # Get the current frame from the drone's video stream
    # img = cap.read()  # Capture frame from external camera (commented out as drone camera is used)
    img = cv2.resize(img, (frameWidth, frameHeight))  # Resize the frame
    img = cv2.flip(img, 0)  # Flip the frame vertically

    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # Convert the frame to HSV color space

    # Get current positions of the trackbars
    h_min = cv2.getTrackbarPos("HUE Min", "HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")

    # Define lower and upper bounds for the HSV values
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    mask = cv2.inRange(imgHsv, lower, upper)  # Create a mask based on the HSV range
    result = cv2.bitwise_and(img, img, mask=mask)  # Apply the mask to the original frame

    print(f'[{h_min},{s_min},{v_min},{h_max},{s_max},{v_max}]')  # Print the HSV values

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)  # Convert mask to BGR format for stacking
    hStack = np.hstack([img, mask, result])  # Stack the original frame, mask, and result horizontally

    cv2.imshow('Horizontal Stacking', hStack)  # Display the stacked frames

    if cv2.waitKey(1) and 0xFF == ord('q'):  # Break the loop if 'q' key is pressed
        break

# cap.release()  # Release the external camera (commented out as drone camera is used)
cv2.destroyAllWindows()  # Destroy all OpenCV windows
