import keyboard
import pyautogui as pag
from tkinter import *
import time
import subprocess
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from PIL import Image
# new imports due to revisions
import threading
from itertools import combinations_with_replacement
import win32gui
import psutil
import configparser
import os
import ast

# Variables

pag.PAUSE = 0.005
last_reroll_time = 0
is_rolling = False  # Flag to indicate if the program is actively rolling
star_limit = 0
starforce_buttons = [
    "img/function/enhance.png",
    "img/function/sfok.png",
    "img/function/enhance2.png",
    "img/function/reveal.png",
]
starforce_conditions = [
    "img/function/10star.png",
    "img/function/15star.png",
    "img/function/disablestarcatch.png",
    "img/function/enablestarcatch.png",
]

# Defined Functions


# Image locator + click
def find_and_click_image(image_path, confidence):
    image_location = pag.locateCenterOnScreen(image_path, region=region, confidence=confidence)
    if image_location is not None and is_rolling:
        pag.click(image_location)
        return True
    return False

# Focus MapleStory - currently disfunctional, issue with win32gui module
def focus_maplestory_window():
    # Replace with the actual MapleStory process name
    target_process_name = "MapleStory.exe"
    target_window_handle = None

    def callback(window_handle, process_list):
        try:
            process_id = win32gui.GetWindowThreadProcessId(window_handle)[1]
            process = psutil.Process(process_id)
            if process.name() == target_process_name:
                process_list.append(window_handle)
        except Exception as e:
            print(f"Error occurred while enumerating windows: {e}")

    window_handles = []
    win32gui.EnumWindows(callback, window_handles)

    if window_handles:
        # Select the first window found
        target_window_handle = window_handles[0]

    if target_window_handle:
        win32gui.SetForegroundWindow(target_window_handle)

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

        label = ttk.Label(self.tooltip, text=self.text, background="#FFFFE0",
                          relief="solid", borderwidth=1, font=("Arial", 10), wraplength=tooltip_width)
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
    print("Current region: ", region)
    result = subprocess.run(
        ["python", "region_selector.py"], capture_output=True)
    region_str = result.stdout.decode().strip()
    if region_str.startswith("Selected region:"):
        region_str = region_str.replace("Selected region:", "").strip()
        region_str = region_str.replace(
            "(", "").replace(")", "")  # Remove extra parenthesis
        region = tuple(map(int, region_str.split(",")))
        print("New region: ", region)
        save_settings()
        print("Settings saved!")
    else:
        print("Region selection canceled. Keeping the old region values.")
    return region

# Reroll function for cubes
def reroll():
    global last_reroll_time, is_rolling

    while is_rolling:
        initial_position = pag.position()
        current_time = time.time()
        retry_button = pag.locateCenterOnScreen(
            "img/function/conemoretry.png",
            region=region,
            confidence=0.97,
        )
        if current_time - last_reroll_time >= float(cooldown_duration.get()) and retry_button is not None:
            print("Rerolling...")
            outofcube = pag.locateCenterOnScreen(
                "img/function/outofcube.png",
                region=region,
                confidence=0.95,
            )
            if outofcube:
                print("Out of cubes.")
                is_rolling = False
                return

            # focus_maplestory_window() - fix this function
            print(f"Button located at: {retry_button}. Clicking...")
            pag.click(retry_button, clicks=3)
            pag.press('enter', presses=5)
            pag.moveTo(initial_position[0], initial_position[1])
            last_reroll_time = current_time  # Update the last reroll time
            time.sleep(1.3)  # Delay to allow results to show
            return
    return

# Press Ok Button
def press_ok_button():
    global last_reroll_time, is_rolling
    initial_position = pag.position()
    ok_button = pag.locateCenterOnScreen(
        "img/function/ok.png",
        region=region,
        confidence=0.96,
    )
    is_rolling = False #stop rolling
    current_time = time.time()
    # Check if AutoPressOk is enabled and if yes, click the "Ok" button
    if auto_ok_state.get() == "on":
        if current_time - last_reroll_time < float(cooldown_duration.get()): # wait for the delay before clicking will close the cube UI
            time.sleep(float(cooldown_duration.get()) - (current_time - last_reroll_time))
        pag.click(ok_button, clicks=2)
        pag.moveTo(initial_position[0], initial_position[1])
    pag.alert("Done.")
    return


# Calculate Stat function for rolling potentials
def calculate_stat(attribute, total):
    print("Calculating")

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
    while count < total and is_rolling:
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
            press_ok_button()
            return

        print("Insufficient lines found, performing reroll...")
        count = 0  # reset count to zero
        lines = []  # Clear lines
        matched_coordinates.clear()  # Clear matched coordinates
        reroll()



# Automatic Rank Up / Tier Up the current equip to selected rank
def auto_rank(rank):
    print("Tiering up!")

    # Define a dictionary to map ranks to their respective image filenames
    rank_images = {
        "Epic": "img/ranks/epic.png",
        "Unique": "img/ranks/unique.png",
        "Legendary": "img/ranks/ld.png",
    }

    while is_rolling:
        rank_image = rank_images.get(rank)
        if rank_image:
            while True:
                # Locate the rank image
                rank_location = pag.locateCenterOnScreen(
                    rank_image,
                    region=region,
                    confidence=0.96
                )

                if rank_location:
                    print(f"{rank} achieved!")
                    press_ok_button()

        print("Rank not matched. Rerolling...")
        reroll()

# Starforce automation
def auto_starforce(starforce_buttons, star_limit):
    global is_rolling

    while is_rolling:
        for image_path in starforce_buttons:
            initial_position = pag.position()
            image_location = pag.locateOnScreen(
                image_path,
                region=region,
                confidence=0.90,
            )
            if "sfok.png" in image_path:
                pag.click(image_location)
            if "enhance.png" in image_path:
                #find_and_click_image("img/function/sfok.png", confidence=.9)
                pag.click(image_location)
            if image_location is not None:
                pag.click(image_location)
                pag.moveTo(
                    initial_position[0],
                    initial_position[1])
            # if image_location is not None:
            #     if "10star.png" in image_path or "15star.png" in image_path:
            #         if star_limit is not None and int(star_limit) >= 0:
            #             print(
            #                 f"Detected {star_limit} stars. Quitting the function.")
            #             is_rolling = False
            #             break

def auto_craft():
    print("Crafting...")
    global is_rolling
    is_rolling = True
    initial_position = pag.position()

    while is_rolling:
        # Find and click the "Craft" button
        print("Waiting for craft button...")
        while not find_and_click_image("img/function/craft.png",confidence=.97) and is_rolling:
            return

        # Find and click the "Ok" button
        print("Confirming craft!")
        while not find_and_click_image("img/function/craftok.png",confidence=.97) and is_rolling:
            return

        # Find and click the "Ok2" button
        print("Crafting in progress...")
        while not find_and_click_image("img/function/craftok2.png",confidence=.97) and is_rolling:
            return
        pag.moveTo(
            initial_position[0],
            initial_position[1]
        )



# Function to check for the Shift key and update the is_rolling flag
def hotkey_handler():
    global is_rolling
    while True:
        if is_rolling and keyboard.is_pressed('shift'):
            is_rolling = False
            print("Rolling stopped.")
        time.sleep(0.1)
    

# Create a thread for the hotkey handling
hotkey_thread = threading.Thread(target=hotkey_handler)
# Set the thread as a daemon to automatically exit when the main thread exits
hotkey_thread.daemon = True
hotkey_thread.start()

#########################################################################################

# class App(ctk.CTk):
#     def __init__(self):
#         super().__init__()

#         self.title("Maple Util")
#         self.geometry("250x350")
#         self.grid_columnconfigure((0,1,2), weight=1)
#         self.resizable(True,True)
#         self._set_appearance_mode("dark")
#         self.iconbitmap("img/icon/cubeicon.ico")


# Root mainframe GU
ctk.set_appearance_mode("dark")
root = ctk.CTk()
root.iconbitmap("img/icon/cubeicon.ico")
root.geometry("300x350")
root.title("Maple Util")
root.resizable(True, True)

########### Variables

global_padding = 5
auto_ok_state = ctk.StringVar(value="off")
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
cooldown_duration = tk.StringVar()
cooldown_duration.set("1.8")
############### Definitions for GUI

# Save settings function (updated to avoid overwriting the settings file)
def save_settings():
    config = configparser.ConfigParser()

    # Check if the settings file exists
    if os.path.exists('settings.ini'):
        # Read existing settings from the file
        config.read('settings.ini')

    # Update the config with the new settings
    config['General'] = {
        'CooldownDuration': cooldown_duration.get(),
        'AutoOKState': auto_ok_state.get(),
        'GearLevelSetting': gear_level_dropdown.get(),
        'RaritySetting': rarity_dropdown.get(),
        'StarLimitSetting': star_limit_dropdown.get(),
        'StatSetting': attribute_dropdown.get(),
        'TotalValueSelected': total_value_dropdown.get(),
        'RegionArea': region
    }

    # Write the updated settings back to the file
    with open('settings.ini', 'w') as configfile:
        config.write(configfile)    

# Load settings function (updated to avoid overwriting the settings file)
def load_settings():
    global region, auto_ok_state, cooldown_duration  # Add these lines to indicate that we want to modify the global variables

    config = configparser.ConfigParser()

    # Check if the settings file exists
    if os.path.exists('settings.ini'):
        # Read existing settings from the file
        config.read('settings.ini')

    if 'General' not in config:
        # Set default values if the 'General' section is missing
        config['General'] = {
            'CooldownDuration': '1.8',
            'AutoOKState': 'off',
            'GearLevelSetting': 'Low',
            'RaritySetting': 'Epic',
            'StarLimitSetting': '0',
            'StatSetting': 'INT',
            'TotalValueSelected': '3',
            'RegionArea': '(843, 383, 1065, 694)'
        }

    # Load settings from the configuration file or use default values
    cooldown_duration_value = config['General'].getfloat('CooldownDuration', 1.8)
    auto_ok_state.set(config['General'].get('AutoOKState', 'off'))
    gear_level = config['General'].get('GearLevelSetting', 'Low')
    rarity = config['General'].get('RaritySetting', 'Epic')
    star_limit = config['General'].getint('StarLimitSetting', 0)
    attribute = config['General'].get('StatSetting', 'INT')
    total_value = config['General'].get('TotalValueSelected', '3')
    region_str = config['General'].get('RegionArea', '(843, 383, 1065, 694)')
    try:
        region = ast.literal_eval(region_str)
    except (ValueError, SyntaxError):
        print("Error: Failed to parse region from settings. Using default region.")
        region = (843, 383, 1065, 694)

    # Set the default values for the dropdowns if not found in the settings
    if gear_level not in ['Low', 'High']:
        gear_level = 'Low'
    if rarity not in ['Rare', 'Epic', 'Unique', 'Legendary']:
        rarity = 'Epic'

    cooldown_duration.set(cooldown_duration_value)
    gear_level_dropdown.set(gear_level)
    rarity_dropdown.set(rarity)
    star_limit_dropdown.set(star_limit)
    attribute_dropdown.set(attribute)
    total_value_dropdown.set(total_value)
    update_total_value_option()



def checkbox_event():
    print("Automatically close cube UI set to: ", auto_ok_state.get())
    save_settings()


# Label function
def label(text):
    label = ctk.CTkLabel(
        root,
        text=text,
        bg_color="#242424",
    )
    return label

# Update total dropdown value
def update_total_value_option():
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
    if possible_values:
        total_value_dropdown.set(possible_values[0])

# Set Starforce limit
def set_star_limit(limit):
    global star_limit
    star_limit = int(limit)
    save_settings()

# Button callbacks
# Run
def run_button_callback():
    global is_rolling
    is_rolling = True

    while is_rolling:
        calculate_stat(
            attribute_dropdown.get(),
            int(total_value_dropdown.get())
        )

def auto_starforce_callback():
    print("Beginning Starforcing... Press Shift to Stop.")
    global is_rolling
    is_rolling = True

    starforce_thread = threading.Thread(
        target=auto_starforce,
        args=(starforce_buttons, star_limit),
    )
    # Start the thread
    starforce_thread.start()

# tier_up
def tier_up_button_callback():
    print("Tiering up!")
    global is_rolling
    is_rolling = True

    auto_rank(
        rarity_dropdown.get()
    )

# Event Handlers
# Reroll delay
def update_delay(*arg):
    updated_delay = cooldown_duration.get()
    cooldown_duration.set(updated_delay)
    print(f"Cooldown updated to {updated_delay}.")
    save_settings()
# Gear level
def gear_level_changed(*args):
    selected_option = gear_level_dropdown.get()
    update_total_value_option()
    print(f"Gear Level set to {selected_option}.")
    save_settings()
# rarity
def rarity_changed(*args):
    selected_option = rarity_dropdown.get()
    update_total_value_option()
    print(f"Rarity set to {selected_option}.")
    save_settings()

# Dropdown lists (Combobox)

# Gear level dropdown
gear_level_label = label("Gear Level:")
gear_level_label.grid(row=2, column=0)
gear_level_dropdown = ttk.Combobox(root, values=['Low', 'High'], width=5)
gear_level_dropdown.grid(row=2, column=1, sticky="w")
gear_level_dropdown.bind('<<ComboboxSelected>>', gear_level_changed)
# rarity dropdown
rarity_label = label("rarity:")
rarity_label.grid(row=3, column=0)
rarity_dropdown = ttk.Combobox(root, values=['Rare', 'Epic', 'Unique', 'Legendary'], width=9)
rarity_dropdown.grid(row=3, column=1, sticky="w")
rarity_dropdown.bind('<<ComboboxSelected>>', rarity_changed)
# attribute dropdown
attribute_label = label("attribute:")
attribute_label.grid(row=5, column=0)
attribute_dropdown = ttk.Combobox(root, values=attribute_options, width=6)
attribute_dropdown.grid(row=5, column=1, sticky="w")

# Create the total value dropdown
total_value_label = label("Total Value:")
total_value_label.grid(row=6, column=0)
total_value_dropdown = ttk.Combobox(root, width=3)
total_value_dropdown.grid(row=6, column=1, sticky="w")

# Star limit dropdown
star_limit_label = label("Star Limit:")
star_limit_label.grid(
    row=9,
    column=0,
    #padx=global_padding,
    #sticky="e"
)  # No horizontal gap, expand horizontally
star_limit_dropdown = ttk.Combobox(root, values=star_limits, width=3)
star_limit_dropdown.grid(
    row=9, column=1,
    #padx=global_padding, pady=global_padding,
    sticky="w"
    )
star_limit_dropdown.bind("<<ComboboxSelected>>", lambda event: set_star_limit(star_limit_dropdown.get()))
# Auto Starforce button
auto_starforce_button = ctk.CTkButton(
    root,
    text="Auto SF",
    command=auto_starforce_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
)
auto_starforce_button.grid(
    row=9, column=1,
    padx=50,
    sticky="e"
)

# Create buttons
# Select Region button
select_region_button = ctk.CTkButton(
    root, text="Select Region",
    command=select_region,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
    )
select_region_button.grid(row=0, column=0, pady=5)
# Stop hotkey tip
stop_key_label = label("Press Shift to STOP any process.")
stop_key_label.grid(row=1, column=0, columnspan=2, pady=5)

# Tier Up
tier_up_button = ctk.CTkButton(
    root,
    text="Tier Up",
    command=tier_up_button_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    # height=25
)
tier_up_button.grid(row=7, column=0)  # place

# Run
run_button = ctk.CTkButton(
    root,
    text="RUN",
    command=run_button_callback,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    # height=25
)
run_button.grid(row=7, column=1, padx=0)  # place

#auto_craft
auto_craft_button = ctk.CTkButton(
    root,
    text="Auto Craft",
    command=auto_craft,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
)
auto_craft_button.grid(
    row=0, column=1)

# Delay of reroll
# Create the delay label
delay_label = label("Adjust delay of reroll:")
delay_label.grid(row=10, column=0, padx=global_padding, pady=global_padding, sticky="e")
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

auto_ok_checkbox = ctk.CTkCheckBox(
    root, text="Auto OK",
    command=checkbox_event,
    variable=auto_ok_state,
    onvalue="on",
    offvalue="off"
    )
auto_ok_checkbox.grid(row=7, column=2, padx=0)

# Register the hotkey to activate the run button
keyboard.add_hotkey('ctrl+r', run_button_callback)
keyboard.add_hotkey('ctrl+s', auto_starforce_callback)



# Create a dictionary to store widgets and their tooltips
tooltips = {
    auto_craft_button: "Select the item you would like to craft "
                        "and click this button. It will automatically craft whenever "
                        "it detects the green crafting button. Stop with Shift",
    run_button: "CTRL+R will also run the cuber",
    auto_starforce_button: "Hotkey: CTRL+S. Stop with Shift",
    total_value_label: "Select the total value",
    attribute_label: "Select the attribute",
    tier_up_button: "Cube until the selected rarity is obtained",
    delay_label: "Increase the value if the script is rolling too early. "
                "The value is in seconds. "
                "2 seconds should work universally.",
    auto_ok_checkbox: "Tick this box if you want the program to automatically "
    "click OK when finished cubing."
}

# TOOLTIPS
for name, text in tooltips.items():
    tooltip(name, text)

load_settings()
cooldown_duration.trace('w', update_delay)
# Update the total value options initially
update_total_value_option()
root.mainloop()
# app = App()
# app.mainloop()