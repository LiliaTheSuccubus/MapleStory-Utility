import tkinter as tk

def on_drag_start(event):
    global start_x, start_y
    start_x = event.x_root
    start_y = event.y_root

def on_drag_end(event):
    global start_x, start_y, end_x, end_y
    end_x = event.x_root
    end_y = event.y_root
    region = (start_x, start_y, end_x, end_y)
    print(f"Selected region: {region}")
    root.destroy()
    return ','.join(map(str, region))

def close_window(event):
    root.destroy()

root = tk.Tk()
# Make the window fullscreen
root.attributes('-fullscreen', True)
# Make the window borderless and non-resizable
root.overrideredirect(True)
root.attributes('-topmost', True)
# Set window transparency
root.attributes('-alpha', 0.55)

canvas = tk.Canvas(root)
canvas.pack(expand=True, fill="both")

label = tk.Label(
    root,
    text=("Click and drag the dimensions of the cube UI's default position.\n\n"
        "If using other functions, select the entire window.\n"
        "But proceed with caution,\n"
        "As this may cause unintended behavior.\n\n\n\n"
        "You can cancel the selection by pressing Escape."
        ),
    font=("Arial", 14),
    wraplength=500,
    )
label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

canvas.bind("<Button-1>", on_drag_start)
canvas.bind("<ButtonRelease-1>", on_drag_end)

# Set hotkey to cancel without changes
root.bind("<Escape>", close_window)

root.mainloop()