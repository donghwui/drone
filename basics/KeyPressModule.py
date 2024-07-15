import pygame


# init: creates a display window
def init():
    pygame.init()
    win = pygame.display.set_mode((400, 400))


def getKey(keyName):
    ans = False

    # Process all events in the event queue
    for eve in pygame.event.get():
        pass

    # Get the state of all keyboard buttons
    keyInput = pygame.key.get_pressed()

    # Get the specific key code for the given key name (e.g., "LEFT", "RIGHT")
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    # Print the key name for debugging purposes
    print('K_{}'.format(keyName))

    # Check if the specific key is currently being pressed
    if keyInput[myKey]:
        ans = True

    # Update the display
    pygame.display.update()

    return ans

# Check if the left or right arrow key is pressed
def main():
    if getKey("LEFT"):
        print("Left key pressed")
    if getKey("RIGHT"):
        print("Right key Pressed")


if __name__ == "__main__":
    init()
    while True:
        main()
