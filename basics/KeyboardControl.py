from djitellopy import tello
import KeyPressModule as kp
from time import sleep

# init and connect the drone
kp.init()
drone = tello.Tello()
drone.connect()
print(drone.get_battery())


# input: keyboard commands
# output: updated [lr, fb, ud, yv]
def getKeyboardInput():
    # init left-right (lr), forward-backward (fb), up-down (ud), and yaw (yv) movements
    lr, fb, ud, yv = 0, 0, 0, 0
    speed = 50  # speed init

    # Check for key presses and update movement vars
    if kp.getKey("LEFT"):
        lr = -speed  # Move left
    elif kp.getKey("RIGHT"):
        lr = speed  # Move right
    if kp.getKey("UP"):
        fb = speed  # Move forward
    elif kp.getKey("DOWN"):
        fb = -speed  # Move backward
    if kp.getKey("w"):
        ud = speed  # Move up
    elif kp.getKey("s"):
        ud = -speed  # Move down
    if kp.getKey("a"):
        yv = -speed  # Yaw left
    elif kp.getKey("d"):
        yv = speed  # Yaw right

    # Check for landing and takeoff commands
    if kp.getKey("q"):
        drone.land()
        sleep(3)  # Pause for 3 seconds
    if kp.getKey("e"):
        drone.takeoff()

    return [lr, fb, ud, yv]


while True:
    vals = getKeyboardInput()
    drone.send_rc_control(vals[0], vals[1], vals[2], vals[3])
    sleep(0.05)  # pause for 50ms
