import pyautogui

# Function to get mouse click coordinates
def get_click_coordinates():
    print("Please click on the desired location on the screen.")
    print("Press Ctrl+C to stop capturing clicks.")

    try:
        while True:
            x, y = pyautogui.position()
            print(f"Clicked at coordinates: ({x}, {y})")
            yield x, y
    except KeyboardInterrupt:
        print("Click capturing stopped.")

# Function to replay the captured clicks
def replay_clicks(click_coordinates):
    print("Replaying clicks...")

    try:
        while True:
            for x, y in click_coordinates:
                pyautogui.click(x, y)
    except KeyboardInterrupt:
        print("Replay stopped.")

# Main function
def main():
    click_coordinates = list(get_click_coordinates())
    replay_clicks(click_coordinates)

if __name__ == "__main__":
    main()
