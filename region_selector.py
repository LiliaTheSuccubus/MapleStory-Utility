import tkinter as tk

def on_drag_start(event):
    global start_x, start_y
    start_x = event.x_root
    start_y = event.y_root

def on_drag_motion(event):
    global start_x, start_y, end_x, end_y
    end_x = event.x_root
    end_y = event.y_root

def on_drag_end(event):
    global start_x, start_y, end_x, end_y
    region = (start_x, start_y, end_x, end_y)
    print(f"Selected region: {region}")
    root.destroy()
    return ','.join(map(str,region))

root = tk.Tk()

# Set window size and position
root.geometry("300x400+800+320")

# Set window transparency
root.attributes('-alpha', 0.55)

# Set window to always on top
root.attributes('-topmost', True)

canvas = tk.Canvas(root, width=300, height=300)
canvas.pack()

# Add instructions at the bottom
label = tk.Label(root, text="Move Maple until Cube window is under this, then press X.", font=("Arial", 12), wraplength=200)
label.pack(side="bottom", pady=10)

canvas.bind("<Button-1>", on_drag_start)
canvas.bind("<B1-Motion>", on_drag_motion)
canvas.bind("<ButtonRelease-1>", on_drag_end)

root.mainloop()