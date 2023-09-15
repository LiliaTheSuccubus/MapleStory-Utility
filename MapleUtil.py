"""
Todo:

* modular confidence field: adjust confidence without having to restart debugging
* in-window terminal; embedded terminal within the program to eliminate window clutter
* cube counter:
    - session amount (total)
    - current iteration
* optimize calculate_stat function:
    - implement multiconditional calculation
    - condense calculations by eliminating the excess searching of images outside of the specific scope of tier+level
    - add allstat images and write algorithm to consider them in match total
LILIA CUTE MASCOT??? convert an image to ASCII artt for code intro
"""

#############################################
# Imports
#############################################
import keyboard
import pyautogui as pag
from pyautogui import press
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
import concurrent.futures
#############################################
# Variables
#############################################
initial_position = pag.position()
pag.PAUSE = 0.005
last_reroll_time = time.time()
is_rolling = False  # Flag to indicate if the program is actively rolling
star_limit = 0
# Define image names as a list
IMAGE_NAMES = [
    "okgreen",
    "craftok2",
    "craft",
    "yes",
    "extract",
    "fuse",
    "rankupfam",
    "next",
    "confirm"
]

# Define a dictionary to map ranks to their respective image filenames
rank_images = {
    "Rare": "img/ranks/rare.png",
    "Epic": "img/ranks/epic.png",
    "Unique": "img/ranks/unique.png",
    "Legendary": "img/ranks/ld.png",
}

# Define custom confidences for specific images
CUSTOM_CONFIDENCES = {
    "fuse": .97,
    "rankupfam": 0.98
}
# Construct full image paths using f-strings
IMAGE_PATHS = [f"img/function/{name}.png" for name in IMAGE_NAMES]

#############################################
############### Defined Functions
#############################################
def calculate_gear_rarity_values(attribute, rarity, gear_level):
    gear_level_values = base_values[gear_level][rarity]
    return [f"{attribute}{value}" for value in gear_level_values if value != 0]

# Reset cursor position
def reset_cursor():
    pag.moveTo(initial_position[0], initial_position[1])

# Update cursor position
def update_cursor():
    global initial_position
    initial_position = pag.position()

def close_cube_window():
    """
    Features:
    * updates cursor position at start
    * sets rolling flag to False
    * closes cube UI by pressing OK
    """
    update_cursor()
    global is_rolling
    is_rolling = False
    check_cooldown()
    find_and_click_image("img/function/okorange.png", confidence=.9)
    return

# Image locator + click
def find_and_click_image(image_path, n=1, confidence=0.98, debug=False, locate=False):
    """
    Loads image from image_path with default confidence of .98, and clicks it N times.
    :param n:           Number of times to click image.
    :param confidence:  Adjusts matching accuracy.
    :param debug:       Toggles printing a statement with image_path to debug.
    :param locate:      Set to True to skip clicking functionality. Returns True or False.
    :return:            None
    """
    if confidence is None:
        confidence = CUSTOM_CONFIDENCES.get(image_path, 0.98)
    image_location = pag.locateCenterOnScreen(image_path, region=region, confidence=confidence)

    if image_location is not None:
        if locate is True:
            return True
        pag.click(image_location,clicks=n)
        time.sleep(0.05)
        reset_cursor()
    else:
        if debug is True:
            print(f"I didn't find {image_path}! You sure that's the right image? Maybe adjust the confidence ({confidence})!")
        return False

def check_cooldown(): # Doesn't modify any values so global variables SHOULDN'T be needed.
    """
    Waits for  remainder of the reroll cooldown before proceeding
    """
    time_elapsed = time.time() - last_reroll_time
    cooldown_remaining = float(cooldown_duration.get()) - time_elapsed
    if cooldown_remaining > 0:
        time.sleep(cooldown_remaining)
    
def check_rank():
    """
    Acts like a traffic stop; 
    Waits for rank to appear in the cubing window before proceeding.
    """
    rank_found = False

    while rank_found is False and is_rolling:
        for rank, image_path in rank_images.items():
            if pag.locateCenterOnScreen(image_path, region=region, confidence=0.9):
                #print(f"Rank {rank} detected. Proceeding...")
                rank_found = True
                break  # Exit the loop once any rank image is found
    return rank_found
 
# Reroll function for cubes
def reroll():
    """
    Rerolling function for cubing. Has failsafes implemented, so
    there's no need to call other functions to prepare for the usage of reroll.
    
    Features:
    * detects if cubes are exhausted
    * automatically uses cube to reroll potential
    * is cute :3
    """
    global last_reroll_time, is_rolling

    if check_rank():
        outofcube = pag.locateCenterOnScreen("img/function/outofcube.png",region=region,confidence=0.97)
        retry_button = pag.locateOnScreen("img/function/conemoretry.png",region=region,confidence=0.8)
        
        if is_rolling:
            if outofcube:
                print("Out of cubes, boss!")
                if auto_ok_state.get() == "on":
                    close_cube_window()
                else:
                    is_rolling = False # Looping stopped
            
            if retry_button is not None:
                update_cursor()
                check_cooldown()
                # focus_maplestory_window() - fix this thingy so program wont click outside
                pag.click(retry_button, clicks=5)
                pag.press('enter', presses=5)
                print("Okay! I rolled it for ya~!")
                last_reroll_time = time.time()  # Update the last reroll time
                reset_cursor()

# Focus MapleStory - currently disfunctional, issue with win32gui module or skill issue?
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

# OCR project that is incomplete
# # Path to tesseract executable, change this to your local path
# pytesseract.pytesseract.tesseract_cmd=r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# # Function to perform OCR on an image
# def ocr(image_path):
#     img=Image.open(image_path)
#     text=pytesseract.image_to_string(img)
#     return text.strip()

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

def cube_prompt_user():
    """
    Your function description here.
    """
    global last_reroll_time

    if pag.locateCenterOnScreen("img/function/conemoretry.png", region=region, confidence=0.9):
        return
    else:
        print("Ya gotta cube somethin'!")
        while is_rolling:
            update_cursor()
            if is_rolling is False or pag.locateCenterOnScreen("img/function/conemoretry.png", region=region, confidence=0.9):
                return
            if find_and_click_image("img/function/okgreen.png"):
                last_reroll_time = time.time() # Update the last reroll time

# Calculate Stat function for rolling potentials
def calculate_stat():
    """
    
    """
    global is_rolling
    is_rolling = True
    attribute = attribute_dropdown.get()
    total = int(total_value_dropdown.get())
    rarity = rarity_dropdown.get()
    gear_level = gear_level_dropdown.get()
    images = {}
    available_values = calculate_gear_rarity_values(attribute, rarity, gear_level)
    count = 0
    lines = []  # Initialize a list to store the lines found
    matched_coordinates = set()  # Keep track of matched coordinates
    print(available_values)

    for value in available_values:
        img_path = f"img/{value}.png"

        if os.path.exists(img_path):
            images[value] = Image.open(img_path)
        else:
            print(f"Image not found: {img_path}")
    
    cube_prompt_user()
    print(f"So ya want {total} {attribute}? I'll see what I can do!")
    save_settings()
    
    print("Alrighty, gambling time! Haha~")
    while count < total and is_rolling:
        print("I'm mathing...")
        for img_name, img in images.items():
            matches = list(pag.locateAllOnScreen(img, region=region, confidence=0.96))
            line_number = int(img_name.split(f"{attribute}")[-1])
            for match in matches:
                if match not in matched_coordinates:
                    lines.append(line_number)
                    matched_coordinates.add(match)
        count = sum(lines) # Adds up lines for total value
        if is_rolling:
            print(f"I found these numbers: {lines}!")
            print(f"So that's about, uh... {count}?")
        if count >= total:
            print(f"Awesomepossum! We reached the goal of {total} {attribute}!")
            if auto_ok_state.get() == "on":
                close_cube_window()
            else:
                is_rolling = False # Looping stopped
            return
        elif is_rolling:
            print("We didn't get enough, boss... Lemme roll it again!")
            count = 0  # reset count to zero
            lines = []  # Clear lines
            matched_coordinates.clear()  # Clear matched coordinates
            if is_rolling:
                reroll()
            time.sleep(1.25)

# Automatic Rank Up / Tier Up the current equip to selected rank
def auto_rank():
    global is_rolling
    is_rolling = True
    rank = rarity_dropdown.get()
    
    cube_prompt_user()
    print("Tiering up!")
    save_settings()

    while is_rolling:
        check_cooldown()
        if check_rank():
            rank_location = pag.locateCenterOnScreen(rank_images.get(rank), region=region, confidence=0.90)
            if rank_location: # If desired rank is located
                print(f"{rank} achieved!")
                if auto_ok_state.get() == "on":
                    close_cube_window()
                else:
                    is_rolling = False
                return
            elif is_rolling:
                print("Rank not matched.")
                reroll()

# Starforce automation
def auto_starforce():
    print("Beginning Starforcing... Press Shift to Stop.")
    global is_rolling
    is_rolling = True
    star_limit = int(star_limit_dropdown.get())
    print("Starforcing!")

    Buttons = [
        "img/function/enhance.png",
        "img/function/enhance2.png",
        "img/function/sfok.png",
        "img/function/confirmsf.png",
        "img/function/transfer.png"
    ]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while is_rolling:
            update_cursor()
            futures = [executor.submit(find_and_click_image, image_path,1,confidence=.90) for image_path in Buttons]
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

            if not is_rolling:  # Check if is_rolling changed during this iteration
                reset_cursor()
                break  # Break the loop immediately

def auto_craft():
    print("Crafting...")
    global is_rolling
    is_rolling = True

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while is_rolling:  # Loop as long as is_rolling is True
            update_cursor()
            futures = [executor.submit(find_and_click_image, image_path) for image_path in IMAGE_PATHS]
            # Wait for all tasks to complete
            concurrent.futures.wait(futures)

            if not is_rolling:  # Check if is_rolling changed during this iteration
                reset_cursor()
                break  # Break the loop immediately

# Auto reveal function for familiars
def reveal():
    global is_rolling
    is_rolling = True

    while is_rolling:
        find_and_click_image("img/function/reveal.png",confidence=.9)

def spam_click():
    global is_rolling
    is_rolling = True
    update_cursor()
    print("I'm clickin' as fast as I can!")

    while is_rolling:
        pag.click()
        time.sleep(0.01)
    reset_cursor()

def auto_symbol():
    """ Automatically uses the symbols from Arcane River and attempts to equip them. """

    use_active = find_and_click_image("img/inventory/useactive.png", locate=True)
    symbol = symbol_dropdown.get()

    img_path = f"img/symbols/{symbol}.png"
    if os.path.exists(img_path):
        if use_active is False:
            find_and_click_image("img/inventory/use.png")
        find_and_click_image(img_path, 2)
        time.sleep(0.4)
        press('enter')
        time.sleep(.3)
        press('y')
        time.sleep(0.8)
        press('y')
        find_and_click_image("img/inventory/equip.png")
        time.sleep(0.3)
        press('y')
        find_and_click_image(img_path, 2)
        press('enter', presses=2)
    else:
        print(f"No image found for {symbol}")

# Function to check for the Shift key and update the is_rolling flag
def hotkey_handler():
    global is_rolling
    while True:
        if is_rolling and keyboard.is_pressed('shift'):
            is_rolling = False
            print("Functions stopped.")
        time.sleep(0.05)

# Create a thread for the hotkey handling
hotkey_thread = threading.Thread(target=hotkey_handler)
# Set the thread as a daemon to automatically exit when the main thread exits
hotkey_thread.daemon = True
hotkey_thread.start()

#########################################################################################
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
regions = ['VJ', 'CC', 'LL', 'AR', 'MR', 'ES']
gear_level_options = ['Low', 'High']
rank_options = ['Rare', 'Epic', 'Unique', 'Legendary']
attribute_options = ['STR', 'DEX', 'INT', 'LUK', 'ATT', 'MATT']
non_attribute_options = ['ItemDrop', 'MesoObtain', 'SkillCD']
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
cooldown_duration.set("1.80")

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
        'RegionArea': region,
        'WindowDimension': root.geometry()
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
            'CooldownDuration': '1.80',
            'AutoOKState': 'off',
            'GearLevelSetting': 'Low',
            'RaritySetting': 'Epic',
            'StarLimitSetting': '0',
            'StatSetting': 'INT',
            'TotalValueSelected': '3',
            'RegionArea': '(843, 383, 1065, 694)',
            'WindowDimension': '800x600'  # Default window dimension (modify as needed)
        }

    # Load settings from the configuration file or use default values
    cooldown_duration_value = config['General'].getfloat('CooldownDuration', 1.80)
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
    if gear_level not in gear_level_options:
        gear_level = 'Low'
    if rarity not in rank_options:
        rarity = 'Epic'

    cooldown_duration.set(cooldown_duration_value)
    gear_level_dropdown.set(gear_level)
    rarity_dropdown.set(rarity)
    star_limit_dropdown.set(star_limit)
    attribute_dropdown.set(attribute)
    update_total_value_option()
    total_value_dropdown.set(total_value)

    # Set the window dimension (geometry) using root.geometry()
    window_dimension = config['General'].get('WindowDimension', '800x600')
    root.geometry(window_dimension)

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

    # Remove duplicates + Order the values from least to greatest
    possible_values = list(set(possible_values))
    possible_values = sorted(possible_values)

    # Update the options in the total value dropdown
    total_value_dropdown['values'] = possible_values
    if possible_values:
        total_value_dropdown.set(possible_values[0])

###########################################
# Event Handlers
###########################################
# Gear level
def gear_level_changed(*args):
    gear_level_selected = gear_level_dropdown.get()
    update_total_value_option()
    print(f"Gear Level set to {gear_level_selected}.")
    save_settings()
# rarity
def rarity_changed(*args):
    rarity_selected = rarity_dropdown.get()
    update_total_value_option()
    print(f"Rarity set to {rarity_selected}.")
    save_settings()
# attribute
def attribute_changed(*args):
    attribute_selected = attribute_dropdown.get()
    print(f"Attribute set to {attribute_selected}.")
    save_settings()
# total value
def total_value_changed(*args):
    total_value_selected = total_value_dropdown.get()
    print(f"Total Value set to {total_value_selected}.")
    save_settings()
# star limit
def star_limit_changed(*args):
    star_limit_selected = star_limit_dropdown.get()
    print(f"Total Value set to {star_limit_selected}.")
    save_settings()
# symbol region
def symbol_changed(*args):
    symbol_selected = symbol_dropdown.get()
    print(f"Symbol Region set to {symbol_selected}.")
    save_settings()
# reroll delay
def update_delay(*args):
    updated_delay = cooldown_duration.get()
    cooldown_duration.set(updated_delay)
    print(f"Cooldown updated to {updated_delay}.")
    save_settings()

################
# Dropdown lists (Combobox/spinbox)
###############

# Gear level dropdown
gear_level_label=label("Gear Level:")
gear_level_label.grid(row=2, column=0)
gear_level_dropdown=ttk.Combobox(
root,
values=gear_level_options,
width=5)
gear_level_dropdown.grid(
row=2,column=1,sticky="w")
gear_level_dropdown.bind('<<ComboboxSelected>>',gear_level_changed)
# rarity dropdown
rarity_label=label("Rarity:")
rarity_label.grid(row=3,column=0)
rarity_dropdown=ttk.Combobox(root,values=rank_options,width=9)
rarity_dropdown.grid(row=3,column=1,sticky="w")
rarity_dropdown.bind('<<ComboboxSelected>>', rarity_changed)
# attribute dropdown
attribute_label=label("Attribute:")
attribute_label.grid(row=5,column=0)
attribute_dropdown=ttk.Combobox(root,values=attribute_options,width=6)
attribute_dropdown.grid(row=5,column=1,sticky="w")
attribute_dropdown.bind('<<ComboboxSelected>>',lambda event:attribute_changed())
# Create the total value dropdown
total_value_label=label("Total value:")
total_value_label.grid(row=6,column=0)
total_value_dropdown=ttk.Combobox(root,width=3)
total_value_dropdown.grid(row=6,column=1,sticky="w")
total_value_dropdown.bind('<<ComboboxSelected>>',lambda event:total_value_changed())
# Star limit dropdown
star_limit_label=label("Star limit:")
star_limit_label.grid(row=9,column=0)
star_limit_dropdown=ttk.Combobox(root,values=star_limits,width=3)
star_limit_dropdown.grid(row=9,column=1,sticky="w")
star_limit_dropdown.bind('<<ComboboxSelected>>', lambda event: star_limit_changed())
# Symbol dropdown
symbol_label=label("Symbol:")
symbol_label.grid(row=11,column=0)
symbol_dropdown=ttk.Combobox(root,values=regions,width=3)
symbol_dropdown.grid(row=11,column=1,sticky="w")
symbol_dropdown.bind('<<ComboboxSelected>>', lambda event: symbol_changed())

#################
# Create buttons
#################
# Select Region button
select_region_button = ctk.CTkButton(
    root, text="Select Region",
    command=select_region,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
    )
select_region_button.grid(row=0, column=0, pady=5)

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
    row=0, column=1
    )

# Stop hotkey tip
stop_key_label = label("Press Shift to STOP any process.")
stop_key_label.grid(row=1, column=0, columnspan=2, pady=5)

# Tier up button
tier_up_button = ctk.CTkButton(
    root,
    text="Tier Up",
    command=auto_rank,
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
    command=calculate_stat,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=50,
    # height=25
    )
run_button.grid(row=7, column=1, padx=0, sticky="w")  # place

auto_ok_checkbox = ctk.CTkCheckBox(
    root, text="Auto OK",
    command=checkbox_event,
    variable=auto_ok_state,
    onvalue="on",
    offvalue="off"
    )
auto_ok_checkbox.grid(row=7, column=1, padx=0, sticky="e")

# Auto Starforce button
auto_starforce_button = ctk.CTkButton(
    root,
    text="Auto SF",
    command=auto_starforce,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
    )
auto_starforce_button.grid(
    row=9, column=1,
    padx=50,
    sticky="e"
    )

# Delay of reroll
# Create the delay label
delay_label = label("Adjust delay of reroll:")
delay_label.grid(row=10, column=0, padx=global_padding, pady=global_padding, sticky="e")
# Create the delay spinbox
delay_spinbox = tk.Spinbox(
    root,
    from_=0.0,
    to=10.0,
    increment=0.01,
    format="%.2f",
    textvariable=cooldown_duration,
    width=5
    )
delay_spinbox.grid(row=10, column=1, sticky="w")

# Reveal button
reveal_button = ctk.CTkButton(
    root,
    text="Reveal",
    command=reveal,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
    )
reveal_button.grid(
    row=10, column=1,
    padx=50,
    sticky="e"
    )

# Auto Symbol button
symbol_button = ctk.CTkButton(
    root,
    text="Auto Symbol",
    command=auto_symbol,
    fg_color=("#1C1C1C", "#1C1C1C"),
    hover_color=("#424242", "#424242"),
    width=5,
    )
symbol_button.grid(
    row=11, column=1,
    padx=50,
    sticky="e"
    )

# Register the hotkey to activate the run button
keyboard.add_hotkey('ctrl+r', calculate_stat)
keyboard.add_hotkey('ctrl+p', auto_starforce)
keyboard.add_hotkey('ctrl+d', spam_click)

# Create a dictionary to store widgets and their tooltips
tooltips = {
    auto_craft_button: "Select the item you would like to craft "
    "and click this button. I will automatically craft whenever "
    "I detect the green crafting button. Stop with Shift",
    run_button: "CTRL+R will also run the cuber",
    auto_starforce_button: "Hotkey: CTRL+P. Stop with Shift. CTRL+D will spam click instead",
    total_value_label: "Select the total value",
    attribute_label: "Select the attribute",
    tier_up_button: "Cube until the selected rarity is obtained",
    delay_label: "Increase the value if I'm rolling too early! "
    "The value is in seconds. "
    "2 seconds should work universally. Or 2.5 if you have mild lag.",
    auto_ok_checkbox: "Tick this box if you want me to automatically "
    "click OK when finished cubing."
}

# TOOLTIPS
for name, text in tooltips.items():
    tooltip(name, text)

load_settings()
update_cursor()
cooldown_duration.trace('w', update_delay)
root.bind('<Configure>', lambda event: save_settings())
root.mainloop()