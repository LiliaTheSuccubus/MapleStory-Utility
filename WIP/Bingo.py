import time
import pyautogui

def click_bingo_board():
    # Adjust these coordinates based on the position of your bingo board on the screen
    board_x = 500
    board_y = 500
    square_size = 100

    # Click on each square of the bingo board
    for row in range(5):
        for col in range(5):
            square_x = board_x + col * square_size
            square_y = board_y + row * square_size
            pyautogui.click(square_x, square_y)
            time.sleep(0.1)  # Adjust the delay between clicks as needed

def run_auto_bingo():
    while True:
        click_bingo_board()

run_auto_bingo()