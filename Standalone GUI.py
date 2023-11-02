import tkinter as tk
import tkinter.ttk as ttk
import pyautogui as pag
import time
import keyboard
import subprocess
import pytesseract
region=(850, 400, 1100, 700)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
stop_macro = False


def check_stop_key():
    global stop_macro
    if keyboard.is_pressed('space'):
        stop_macro = True

# Prompt user to select region
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
        pag.alert("Error: could not get selected region.")
        region = None
    return region


#Reroll
def reroll(region):
    if keyboard.is_pressed('space'):
        pag.alert("The macro has been stopped.")
        return
    retry = pag.locateCenterOnScreen(".\\img\\function\\conemoretry.png",region=region, confidence=0.96)
    pag.click(retry)
    pag.press('enter', presses=3)
    time.sleep(1.15)

def epicatt(region):
    while True:
        if keyboard.is_pressed('space'):
            pag.alert("The macro has been stopped.")
            break
        a = pag.locateOnScreen(".\\img\\epicatt\\att1.png", region=region, confidence=0.95)
        a1 = pag.locateOnScreen(".\\img\\epicatt\\att2.png", region=region, confidence=0.95)
        a2 = pag.locateOnScreen(".\\img\\epicatt\\att3.png", region=region, confidence=0.80)
        a3 = pag.locateOnScreen(".\\img\\epicatt\\att4.png", region=region, confidence=0.80)
        a4 = pag.locateOnScreen(".\\img\\epicatt\\att5.png", region=region, confidence=0.95)
        if a or a1 or a2 or a3 or a4:
            pag.alert('done!')
            break
        else:
            reroll(region)
            print("Retrying...")
            if keyboard.is_pressed('space'):
                pag.alert("The macro has been stopped.")
                break

# Create your GUI
root = tk.Tk()
root.iconbitmap(".\\img\\icon\\cubeicon.ico")
root.geometry("500x500")
root.title("Test")
root.resizable(True,True)

# Create a button that calls the select_region function
button = tk.Button(root, text="Select Region", command=select_region)
button.pack()

# Create the epicatt button
epicattbutton = ttk.Button(root, text="Epic ATT", command=lambda: epicatt(region))
epicattbutton.pack()

# Initialize the region variable
region = None

root.after(100, check_stop_key)

# Start the GUI main loop
root.configure(bg='black')
root.mainloop()
