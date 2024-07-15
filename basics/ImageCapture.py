from djitellopy import tello
import cv2

drone = tello.Tello()
drone.connect()
print(drone.get_battery())
# streams the frame one by one
drone.streamon()

while True:
    # resize each individual image so it processes faster!
    img = drone.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow('Image', img)  # create window to display the result
    cv2.waitKey(1)  # delay of 1ms
    
