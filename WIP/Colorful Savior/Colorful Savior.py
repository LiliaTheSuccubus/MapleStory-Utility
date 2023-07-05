import pyautogui
from PIL import Image
import time
import subprocess
import sys
import os
import keyboard
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

region = (496, 504, 622, 649)
is_running = False

# Specify the relative path to the image files
green_image_path = "img/green.png"
red_image_path = "img/red.png"
blue_image_path = "img/blue.png"

# Select Region for Cuber
def select_region():
    global region
    result = subprocess.run(["python", "region_selector.py"], capture_output=True)
    region_str = result.stdout.decode().strip()
    if region_str.startswith("Selected region:"):
        region_str = region_str.replace("Selected region:", "").strip()
        region_str = region_str.replace("(", "").replace(")", "")  # Remove extra parenthesis
        region = tuple(map(int, region_str.split(",")))
        print(region)
    else:
        print("Region selection canceled. Keeping the old region values.")
    return region

def main():
    global region, is_running
    if region is None:
        region = select_region()
        pass
    else:
        pass
    
    while True:
        if is_running:
            # Take a screenshot of the selected region
            screenshot = pyautogui.screenshot(region=region)

            # Compare the screenshot with the images using locateOnScreen
            if pyautogui.locateCenterOnScreen(
                green_image_path,
                region=region,
                confidence=0.86
            ):
                print("Green image found!")
                pyautogui.press("left")
                print("Left arrow key pressed!")
            elif pyautogui.locateCenterOnScreen(
                red_image_path,
                region=region,
                confidence=0.86
            ):
                print("Red image found!")
                pyautogui.press("up")
                print("Up arrow key pressed!")
            elif pyautogui.locateCenterOnScreen(
                blue_image_path,
                region=region,
                confidence=0.86
            ):
                print("Blue image found!")
                pyautogui.press("right")
                print("Right arrow key pressed!")
            # time.sleep(0.02)
        # else:
        #     time.sleep(0.1)

def restart_script():
    python = sys.executable
    os.execl(python, python, *sys.argv)

class FileModifiedHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.realpath(__file__):
            print("Script modified. Restarting...")
            observer.stop()
            restart_script()

def toggle_script():
    global is_running
    is_running = not is_running

if __name__ == "__main__":
    # Register the hotkey to toggle the script
    keyboard.add_hotkey("ctrl+r", toggle_script)

    event_handler = FileModifiedHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.realpath(__file__)), recursive=False)
    observer.start()

    try:
        main()
    except KeyboardInterrupt:
        observer.stop()

    observer.join()