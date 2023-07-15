import keyboard
import pyautogui as pag
from tkinter import *
import time
import subprocess
from tkinter import ttk
import tkinter as tk
import customtkinter as ctk
from PIL import Image
# addition to code
import threading
from itertools import combinations_with_replacement

## Variables

pag.PAUSE = 0.005
region = (843, 383, 1065, 694)
last_reroll_time = 0
is_rolling = False  # Flag to indicate if the program is actively rolling
star_limit = 0
starforce_buttons = [
    "img/function/enhance.png",
    "img/function/sfok.png",
    "img/function/enhance2.png",
]
starforce_conditions = [
   "img/function/10star.png",
   "img/function/15star.png",
   "img/function/disablestarcatch.png",
   "img/function/enablestarcatch.png",
]

# Tooltips when hovering on buttons
class tooltip:
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
    global last_reroll_time, is_rolling

    while is_rolling:
        current_time = time.time()
        if current_time - last_reroll_time >= float(cooldown_duration.get()):
            print("Rerolling...")
            outofcube = pag.locateCenterOnScreen("img/function/outofcube.png", region=region, confidence=0.96)
            if outofcube:
                print("Out of cubes.")
                is_rolling = False
                return False
            
            retry_button = None
            while retry_button is None:
                retry_button = pag.locateCenterOnScreen(
                   "img/function/conemoretry.png",
                   region=region,
                   confidence=0.96,
                   )
                print(f"Button located at: {retry_button}. Clicking...")
                pag.click(retry_button, clicks=3)
                pag.press('enter', presses=5)
                print("Confirmed. Waiting for result...")
                time.sleep(1.3)
                last_reroll_time = current_time  # Update the last reroll time
                return True
    return False

# Calculate Stat function for rolling potentials
def calculate_stat(attribute, total):
    global last_reroll_time, is_rolling
    current_time = None

    images = {
        "attribute3": f"img/{attribute}3.png",
        "attribute6": f"img/{attribute}6.png",
        "attribute9": f"img/{attribute}9.png",
        "attribute12": f"img/{attribute}12.png"
    }

    count = 0
    lines = []  # Initialize a list to store the lines found
    matched_coordinates = set()  # Keep track of matched coordinates

    print("Calculate Function.")

    for img_name, img_path in images.items():
        try:
            img = Image.open(img_path)
        except FileNotFoundError:
            print(f"Image not found: {img_path}")
            continue

        matches = list(
            pag.locateAllOnScreen(img, region=region, confidence=0.97)
        )
        line_number = int(img_name.split("attribute")[-1])
        for match in matches:
            if match not in matched_coordinates:
                lines.append(line_number)
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
        #pag.click(ok_button, clicks=3)
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
def auto_starforce(starforce_buttons, star_limit):
    global is_rolling
    while is_rolling:
        for image_path in starforce_buttons:
            image_location = pag.locateCenterOnScreen(image_path, region=region, confidence=0.6)
            if image_location is not None:
                print(image_path)
                if "10star.png" in image_path or "15star.png" in image_path:
                    if star_limit is not None and int(star_limit) >= 0:
                        print(f"Detected {star_limit} stars. Quitting the function.")
                        is_rolling = False
                        break
                pag.click(image_location.x + 10, image_location.y + 5)

def start_auto_starforce():
    global is_rolling
    # Reset the is_rolling flag to True
    is_rolling = True
    # Create a thread for the auto_starforce function
    starforce_thread = threading.Thread(target=auto_starforce, args=(starforce_buttons, star_limit))
    # Start the thread
    starforce_thread.start()

def hotkey_handler():
    global is_rolling
    while True:
        if keyboard.is_pressed('shift') and is_rolling:
            is_rolling = False
            print("Rolling stopped.")
        time.sleep(0.001)

hotkey_thread = threading.Thread(target=hotkey_handler)
hotkey_thread.daemon = True  # Set the thread as a daemon to automatically exit when the main thread exits
hotkey_thread.start()

#########################################################################################

# Root mainframe GUI

ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.iconbitmap("img/icon/cubeicon.ico")
root.geometry("250x270")
root.title("Practice")
root.resizable(True, True)

## Variables
star_limits = [0, 10, 15]  # Available star limits
attribute_options = ['STR', 'DEX', 'INT', 'LUK', 'ATT', 'MATT']
# Base values for potential lines
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

## Definitions
# Update total dropdown value
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
# Set Starforce limit
def set_star_limit(limit):
    global star_limit
    star_limit = int(limit)

## Button callbacks
# Run
def run_button_callback():
    global is_rolling
    is_rolling = True
    calculate_stat(
        attribute_dropdown.get(),
        int(total_value_dropdown.get())
    )

# Starforce
def autostarforce_callback():
    print("Starforcing started.")
    global star_limit

    while is_rolling:  # Loop while is_rolling is True
        auto_starforce(starforce_buttons, star_limit)

    print("Starforcing stopped.")

# Tierup
def tierup_button_callback():
    auto_rank(
        rarity_dropdown.get()
    )

## Event Handlers
# Reroll delay
def update_delay(*arg):
    updated_delay = cooldown_duration.get()
    cooldown_duration.set(updated_delay)
    print(f"Cooldown updated to {updated_delay}.")
# Gear level
def gear_level_changed(*args):
    selected_option = gear_level_dropdown.get()
    update_total_value_options()
    print(f"Gear Level set to {selected_option}.")
# Rarity
def rarity_changed(*args):
    selected_option = rarity_dropdown.get()
    update_total_value_options()
    print(f"Rarity set to {selected_option}.")

# Select Region button
select_region_button=ttk.Button(root, text="Select Region", command=select_region)
select_region_button.grid(row=0, column=0, columnspan=2, pady=5)

# Stop hotkey tooltip
label = tk.Label(root, text="Press Shift to STOP any process.", bg="#242424", fg="white")
label.grid(row=1, column=0, columnspan=2, pady=5)

## Dropdown lists (Combobox)

# Gear level dropdown
gear_level_label = ttk.Label(root, text="Gear Level:")
gear_level_label.grid(row=2, column=0)
gear_level_dropdown = ttk.Combobox(root, values=['Low', 'High'], width=5)
gear_level_dropdown.grid(row=2, column=1, sticky="w")
gear_level_dropdown.bind('<<ComboboxSelected>>', gear_level_changed)
# Rarity dropdown
rarity_label = ttk.Label(root, text="Rarity:")
rarity_label.grid(row=3, column=0)
rarity_dropdown = ttk.Combobox(root, values=['Rare', 'Epic', 'Unique', 'Legendary'], width=9)
rarity_dropdown.grid(row=3, column=1, sticky="w")
rarity_dropdown.bind('<<ComboboxSelected>>', rarity_changed)
# Attribute dropdown
attribute_label = ttk.Label(root, text="Attribute:")
attribute_label.grid(row=5, column=0)
attribute_dropdown = ttk.Combobox(root, values=attribute_options, width=6)
attribute_dropdown.grid(row=5, column=1, sticky="w")
attribute_tooltip = tooltip(attribute_label, "Select the attribute.")
# Create the total value dropdown
total_value_label = ttk.Label(root, text="Total Value:")
total_value_label.grid(row=6, column=0)
total_value_dropdown = ttk.Combobox(root, width=3)
total_value_dropdown.grid(row=6, column=1, sticky="w")
total_value_tooltip = tooltip(total_value_label, "Select the total value.")
# Star limit dropdown
star_limit_label = ttk.Label(root, text="Star Limit:")
star_limit_label.grid(row=9, column=0, padx=1, sticky="e")  # No horizontal gap, expand horizontally
star_limit_dropdown = ttk.Combobox(root, values=star_limits, width=3)
star_limit_dropdown.grid(row=9, column=1, padx=(5, 15), pady=(0, 0), sticky="w")
star_limit_dropdown.bind("<<ComboboxSelected>>", lambda event: set_star_limit(star_limit_dropdown.get()))
# Set dropdown default options
gear_level_dropdown.set('Low')
rarity_dropdown.set('Epic')
star_limit_dropdown.set('0')
attribute_dropdown.set('INT')
total_value_dropdown.set('3')

## Create buttons
# Tier Up
tierup = ctk.CTkButton(
    root,
    text="Tier Up",
    command=tierup_button_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    #height=25
)
tierup.grid(row=7, column=0, padx=0) #place
tierup_tooltip = tooltip(tierup, "Cube until the selected Rarity is obtained.")
# Run
run_button = ctk.CTkButton(
    root,
    text="RUN",
    command=run_button_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    #height=25
)
run_button.grid(row=7, column=1, padx=0, sticky="w") #place
run_button_tooltip = tooltip(run_button, "CTRL+R will also Run the Cuber.")
# Auto Starforce
auto_starforce_button = ctk.CTkButton(
   root,
   text="Auto SF",
   command=autostarforce_callback,
   fg_color=("#1C1C1C", "#1C1C1C"),
   hover_color=("#424242", "#424242"),
   width=5,
)
auto_starforce_button.grid(row=9, column=1, columnspan=2, padx=(50,0), sticky="e")
auto_starforce_button_tooltip = tooltip(auto_starforce_button, "Stop with Shift.")

## Delay of reroll

# Create the cooldown duration variable and set trace (event handler)
cooldown_duration = tk.StringVar()
cooldown_duration.set("1.8")
cooldown_duration.trace('w', update_delay)
# Create the delay label
delay_label = tk.Label(root, text="Adjust delay of reroll:")
delay_label.grid(row=10, column=0, padx=5, sticky="e")
delay_label_tooltip = tooltip(delay_label, "Increase the value if the script is rolling too early. The value is in seconds. 2 seconds should work universally.")
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
delay_spinbox.grid(row=10, column=1, sticky="w")

# Register the hotkey to activate the run button
keyboard.add_hotkey('ctrl+r', run_button_callback)  
# pag.add_hotkey("ctrl", "e", tierup_button_callback)
keyboard.add_hotkey('ctrl+s', start_auto_starforce)

# Update the total value options initially
update_total_value_options()

# Start the Tkinter event loop
root.mainloop()