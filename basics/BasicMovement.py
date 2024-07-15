from djitellopy import tello
from time import sleep

# create a tello object and connect
drone = tello.Tello()
drone.connect()

print(drone.get_battery())  # current battery

# drone takes off
drone.takeoff()
# goes fwd for 2 seconds
drone.send_rc_control(0, 30, 0, 0)
sleep(2)
# drone is stationary when landing, like a helicopter rather than an airplane
drone.send_rc_control(0, 0, 0, 0)
drone.land()  # drone lands
