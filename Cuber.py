import keyboard
import pyautogui as pag
from tkinter import *
import time
import random
import customtkinter
import os
import datetime
import numpy as np
import subprocess
from tkinter import ttk
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image
#MooMoo addition
import pytesseract
import cv2
import win32api, win32con
from win32api import *
import win32gui
import threading
from itertools import combinations_with_replacement
pag.PAUSE = 0.005
region = (843, 383, 1065, 694)
last_reroll_time = 0
is_rolling = False  # Flag to indicate if the program is actively rolling
starforce_buttons = [
   "img/function/10star.png",
   "img/function/enhance.png",
   "img/function/sfok.png",
   "img/function/enhance2.png",
   ]

# Tooltips when hovering on buttons
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        # Create a temporary label to determine the required width for text wrapping
        temp_label = ttk.Label(root, text=self.text, font=("Arial", 10))
        temp_label.update_idletasks()
        temp_label_width = temp_label.winfo_reqwidth()
        temp_label.destroy()

        # Adjust the tooltip width based on the wrapped text width
        tooltip_width = min(temp_label_width, 300)

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")

        label = ttk.Label(self.tooltip, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1, font=("Arial", 10), wraplength=tooltip_width)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# Cancel Reroll and any future function that runs on loops
def cancel_reroll():
    global is_rolling
    if is_rolling:
        # If the program is rolling, abort rolling
        is_rolling = False
        print("Functions stopped.")
        return False
keyboard.add_hotkey('shift', cancel_reroll)

""" OCR project that is incomplete
# Path to tesseract executable, change this to your local path
pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Function to perform OCR on an image
def ocr(image_path):
    img=Image.open(image_path)
    text=pytesseract.image_to_string(img)
    return text.strip()
"""

# Select Region for utility
def select_region():
    global region
    result=subprocess.run(["python", "region_selector.py"], capture_output=True)
    region_str=result.stdout.decode().strip()
    if region_str.startswith("Selected region:"):
        region_str=region_str.replace("Selected region:", "").strip()
        region_str=region_str.replace("(", "").replace(")", "")  # Remove extra parenthesis
        region=tuple(map(int, region_str.split(",")))
        print(region)
    else:
        print("Region selection canceled. Keeping the old region values.")
    return region

# Reroll function for cubes
def reroll(region):
    global last_reroll_time
    global is_rolling
    current_time = None

    while is_rolling:
        current_time = time.time()
        if current_time - last_reroll_time >= float(cooldown_duration.get()): # Only reroll if certain time has elapsed to prevent clicking too early
            print("Rerolling...")
            outofcube = pag.locateCenterOnScreen("img/function/outofcube.png", region=region, confidence=0.96)
            if outofcube:
                print("Out of cubes.")
                is_rolling = False
                return False

            retry_button = pag.locateCenterOnScreen("img/function/conemoretry.png", region=region, confidence=0.96)
            pag.click(retry_button, clicks=3)
            pag.press('enter', presses=3)
            time.sleep(1.5)
            last_reroll_time = current_time  # Update the last reroll time
            return True
        
    return False

# Calculate and read rolled potential lines
def calculate_stat(attribute, total):
    global last_reroll_time
    global is_rolling
    current_time = None

    attribute3_img = Image.open(f"img/{attribute}3.png")
    attribute6_img = Image.open(f"img/{attribute}6.png")
    count = 0
    lines = []  # Initialize a list to store the lines found
    matched_coordinates = set()  # Keep track of matched coordinates

    print("Calculate Function.")

    while count < total and is_rolling:
        attribute3_matches = list(
            pag.locateAllOnScreen(attribute3_img, region=region, confidence=0.97)
            )
        attribute6_matches = list(
            pag.locateAllOnScreen(attribute6_img, region=region, confidence=0.97)
            )

        for match in attribute3_matches:
            if match not in matched_coordinates:
                lines.append(3)
                matched_coordinates.add(match)

        for match in attribute6_matches:
            if match not in matched_coordinates:
                lines.append(6)
                matched_coordinates.add(match)

        count = sum(lines)

        print(f"Lines found: {lines}")
        print(f"Current total: {count}")

        if count >= total: 
            print(f"{attribute} {count} reached!")
            is_rolling = False
            ok_button = pag.locateCenterOnScreen("img/function/ok.png", region=region, confidence=0.96)
            current_time = time.time()
            if current_time - last_reroll_time < float(cooldown_duration.get()):
                print("Waiting for cooldown...")
                time.sleep(float(cooldown_duration.get()) - (current_time - last_reroll_time))
            pag.click(ok_button, clicks=3)
            pag.alert("Done.")
            return 

        print("Insufficient lines found, performing reroll...")
        count = 0  # reset count to zero
        lines = []  # Clear lines
        matched_coordinates.clear()  # Clear matched coordinates
        if not reroll(region):
            return

# Automatic Rank Up / Tier Up the current equip to selected rank
def auto_rank(rank):

    if rank == "Epic":
     while True:
      epicrank=pag.locateCenterOnScreen("img/ranks/epic.png",region=region, confidence=0.96)
      if epicrank:
       pag.alert(f"{rank} achieved!")
       return
      if not reroll(region):
        return

    elif rank == "Unique":
     while True:
      uniquerank=pag.locateCenterOnScreen("img/ranks/unique.png",region=region, confidence=0.96)
      if uniquerank:
       pag.alert(f"{rank} achieved!")
       return
      if not reroll(region):
        return
      
    elif rank == "Legendary":
     while True:
      legendrank=pag.locateCenterOnScreen("img/ranks/ld.png",region=region, confidence=0.96)
      if legendrank:
       pag.alert(f"{rank} achieved!")
       return
      if not reroll(region):
        return

# Starforce automation
def auto_starforce(starforce_buttons):
    star_limit = False

    def search_and_click(image_path):
        nonlocal star_limit
        image_location = pag.locateCenterOnScreen(image_path, region=region, confidence=0.5)
        if image_location is not None:
            print(image_path)
            if "10star.png" in image_path:
                print("10 stars reached.")
                star_limit = True  # Set the flag to stop other threads
                return  # Quit the function
            if star_limit is False:  # Check the flag before executing the click action
                pag.click(image_location.x + 20, image_location.y)

    threads = []
    for image_path in starforce_buttons:
        t = threading.Thread(target=search_and_click, args=(image_path,))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()


#########################################################################################

# Root mainframe GUI

customtkinter.set_appearance_mode("dark")
root = ctk.CTk()
root.iconbitmap("img/icon/cubeicon.ico")
root.geometry("200x250")
root.title("Practice")
root.resizable(True, True)
#root.lift

## Definitions

attribute_options = ['STR', 'DEX', 'INT', 'LUK', 'ATT', 'MATT']

# Define the base possible values for each rarity and gear level
base_values = {
    'Low': {
        'Rare': [0, 3],
        'Epic': [0, 3, 6],
        'Unique': [0, 6, 9],
        'Legendary': [0, 9, 12]
    },
    'High': {
        'Rare': [0, 4],
        'Epic': [0, 4, 7],
        'Unique': [0, 7, 10],
        'Legendary': [0, 10, 13]
    }
}

def run_button_callback():
    global is_rolling
    is_rolling = True
    calculate_stat(
        attribute_dropdown.get(),
        int(total_value_dropdown.get())
    )

def autostarforce_callback():
    print("starting auto sf")
    global is_rolling
    is_rolling = True
    auto_starforce(starforce_buttons)

# Update cooldown_duration delay
def update_delay(*arg):
    updated_delay = cooldown_duration.get()
    cooldown_duration.set(updated_delay)
    print(f"Cooldown updated to {updated_delay}.")

def tierup_button_callback():
    auto_rank(
        rarity_dropdown.get()
    )

# Event handler for gear level change
def gear_level_changed(*args):
    selected_option = gear_level_dropdown.get()
    update_total_value_options()
    print(f"Gear Level set to {selected_option}.")

# Event handler for rarity change
def rarity_changed(*args):
    selected_option = rarity_dropdown.get()
    update_total_value_options()
    print(f"Rarity set to {selected_option}.")

# Update the possible total values based on the selected gear level and rarity
def update_total_value_options():
    gear_level = gear_level_dropdown.get()
    rarity = rarity_dropdown.get()

    # Get the base values for the selected gear level and rarity
    values = base_values[gear_level][rarity]

    # Calculate the possible total values by generating all combinations
    possible_values = []
    for r in range(1, len(values) + 1):
        combinations = combinations_with_replacement(values, r)
        totals = [sum(combination) for combination in combinations]
        possible_values.extend(total for total in totals if total != 0)

    # Remove duplicates
    possible_values = list(set(possible_values))

    # Order the values from least to greatest
    possible_values = sorted(possible_values)

    # Update the options in the total value dropdown
    total_value_dropdown['values'] = possible_values


# Create a button on the GUI
select_region_button=ttk.Button(root, text="Select Region", command=select_region)

# Place the button on the GUI
select_region_button.grid(row=0, column=0, columnspan=2, pady=5)

label = tk.Label(root, text="Press Shift to STOP", bg="#242424", fg="white")
label.grid(row=1, column=0, columnspan=2, pady=5)

## Dropdown lists (Combobox)

## Buttons

# Create the gear level dropdown
gear_level_label = ttk.Label(root, text="Gear Level:")
gear_level_label.grid(row=2, column=0)
gear_level_dropdown = ttk.Combobox(root, values=['Low', 'High'], width=5)
gear_level_dropdown.grid(row=2, column=1)
gear_level_dropdown.bind('<<ComboboxSelected>>', gear_level_changed)

# Create the rarity dropdown
rarity_label = ttk.Label(root, text="Rarity:")
rarity_label.grid(row=3, column=0)
rarity_dropdown = ttk.Combobox(root, values=['Rare', 'Epic', 'Unique', 'Legendary'], width=9)
rarity_dropdown.grid(row=3, column=1)
rarity_dropdown.bind('<<ComboboxSelected>>', rarity_changed)

# Tier Up button
tierup = customtkinter.CTkButton(
    root,
    text="Tier Up",
    command=tierup_button_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    height=25
)
tierup_tooltip = Tooltip(tierup, "Cube until the selected Rarity is obtained.")

# Create the attribute dropdown
attribute_label = ttk.Label(root, text="Attribute:")
attribute_label.grid(row=5, column=0)
attribute_dropdown = ttk.Combobox(root, values=attribute_options, width=6)
attribute_dropdown.grid(row=5, column=1, sticky=tk.E)
attribute_tooltip = Tooltip(attribute_label, "Select the attribute.")

# Create the total value dropdown
total_value_label = ttk.Label(root, text="Total Value:")
total_value_label.grid(row=6, column=0)
total_value_dropdown = ttk.Combobox(root, width=3)
total_value_dropdown.grid(row=6, column=1, sticky=tk.E)
total_value_tooltip = Tooltip(total_value_label, "Select the total value.")

# Run button
run_button = ctk.CTkButton(
    root,
    text="RUN",
    command=run_button_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    height=25
)

tierup.grid(row=7, column=0, columnspan=1, pady=5, sticky=tk.W+tk.E)
run_button.grid(row=7, column=1, columnspan=1, pady=5)
run_button_tooltip = Tooltip(run_button, "CTRL+R will also Run the Cuber.")

# Auto Starforce
auto_starforce_button = ctk.CTkButton(
   root,
   text="Auto SF",
   command=autostarforce_callback,
   fg_color=("#1C1C1C", "#1C1C1C"),
   hover_color=("#424242", "#424242"),
   width=50,
   height=25,
)
auto_starforce_button.grid(row=7, column=2, columnspan=1, pady=5)
auto_starforce_button_tooltip = Tooltip(auto_starforce_button, "Stop with Shift.")

## SpinBox Delay

# Create the cooldown duration variable
cooldown_duration = tk.StringVar()
cooldown_duration.set("1.8")
cooldown_duration.trace('w', update_delay)

# Create the delay label
delay_label = tk.Label(root, text="Adjust delay of reroll:")
delay_label.grid(row=10, column=0, columnspan=2, pady=5)
delay_label_tooltip = Tooltip(delay_label, "Increase the value if the script is rolling too early. The value is in seconds. 2 seconds should work universally.")

# Create the delay spinbox
delay_spinbox = tk.Spinbox(
    root,
    from_=0.0,
    to=10.0,
    increment=0.1,
    format="%.1f",
    textvariable=cooldown_duration,
    width=5
)
delay_spinbox.grid(row=11, column=0, columnspan=2, pady=5)

# Register the hotkey to activate the run button
# keyboard.add_hotkey('CTRL', 'R', run_button_callback)  
# pag.add_hotkey("ctrl", "e", tierup_button_callback)

# Register hotkey 

# Initialize the dropdowns
gear_level_dropdown.set('Low')
rarity_dropdown.set('Epic')

# Update the total value options initially
update_total_value_options()

# Start the Tkinter event loop
root.mainloop()