import Quartz
import time
import threading
import pyautogui
from tkinter import Tk, StringVar, Button, OptionMenu
from tkinter.ttk import Label, Frame, Style
import queue
from pynput import mouse
from pynput.mouse import Listener

IDLE_TIME = 4 * 60

def get_last_activity_time():
    return time.time()

def is_system_idle(last_activity_time):
    return (time.time() - last_activity_time) >= IDLE_TIME

def move_cursor(q):
    last_activity_time = get_last_activity_time()

    def on_move(x, y):
        nonlocal last_activity_time
        last_activity_time = get_last_activity_time()

    def on_click(x, y, button, pressed):
        nonlocal last_activity_time
        last_activity_time = get_last_activity_time()

    def on_scroll(x, y, dx, dy):
        nonlocal last_activity_time
        last_activity_time = get_last_activity_time()

    with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
        while True:
            try:
                q.get_nowait()
                break
            except queue.Empty:
                pass

            if is_system_idle(last_activity_time):
                try:
                    pyautogui.moveRel(10, 10, duration=0.25)
                    pyautogui.moveRel(-10, -10, duration=0.25)
                except pyautogui.FailSafeException:
                    screen_width, screen_height = pyautogui.size()
                    pyautogui.FAILSAFE = False
                    pyautogui.moveTo(screen_width / 2, screen_height / 2)
                    pyautogui.FAILSAFE = True
                    print("Fail-safe triggered. Moving cursor to the center of the screen.")
                last_activity_time = get_last_activity_time()

            time.sleep(2)

def start_thread():
    global q, thread
    q = queue.Queue()
    thread = threading.Thread(target=move_cursor, args=(q,))
    thread.start()

def stop_thread():
    if thread:
        q.put(True)
        thread.join()

def increase_idle_time():
    global IDLE_TIME
    IDLE_TIME += 60
    idle_time_var.set(f"Idle Time: {IDLE_TIME//60} minutes")

def decrease_idle_time():
    global IDLE_TIME
    if IDLE_TIME > 60:
        IDLE_TIME -= 60
        idle_time_var.set(f"Idle Time: {IDLE_TIME//60} minutes")


def update_movement_label():
    minutes = IDLE_TIME // 60
    seconds = IDLE_TIME % 60
    movement_label_text.set(f"Intermittent movement after {minutes} minutes {seconds} seconds of inactivity")

def increase_idle_time_minutes():
    global IDLE_TIME
    IDLE_TIME += 60
    idle_time_var.set(f"Idle Time: {IDLE_TIME // 60} minutes {IDLE_TIME % 60} seconds")

    update_movement_label()

def decrease_idle_time_minutes():
    global IDLE_TIME
    if IDLE_TIME >= 60:
        IDLE_TIME -= 60
        idle_time_var.set(f"Idle Time: {IDLE_TIME // 60} minutes {IDLE_TIME % 60} seconds")
        update_movement_label()

def increase_idle_time_seconds():
    global IDLE_TIME
    IDLE_TIME += 1
    idle_time_var.set(f"Idle Time: {IDLE_TIME // 60} minutes {IDLE_TIME % 60} seconds")
    update_movement_label()

def decrease_idle_time_seconds():
    global IDLE_TIME
    if IDLE_TIME > 0:
        IDLE_TIME -= 1
        idle_time_var.set(f"Idle Time: {IDLE_TIME // 60} minutes {IDLE_TIME % 60} seconds")
        update_movement_label()

def update_idle_time(delta_seconds):
    global IDLE_TIME
    IDLE_TIME = max(0, IDLE_TIME + delta_seconds)
    idle_time_var.set(f"Idle Time: {IDLE_TIME // 60} minutes {IDLE_TIME % 60} seconds")
    update_movement_label()


root = Tk()
root.title("Magic Mouse")
root.geometry("450x250")

style = Style()
style.configure("TButton", font=("Arial", 12), padding=10)
style.configure("TLabel", font=("Arial", 12))

frame = Frame(root, padding="10 10 10 10")
frame.pack(fill="both", expand=True)

movement_label_text = StringVar()
update_movement_label()
Label(frame, textvariable=movement_label_text).grid(row=0, column=0, columnspan=4, pady=10)

idle_time_var = StringVar()
idle_time_var.set(f"Idle Time: {IDLE_TIME // 60} minutes {IDLE_TIME % 60} seconds")
Label(frame, textvariable=idle_time_var).grid(row=3, column=0, padx=10, pady=10)

time_unit_var = StringVar()
time_unit_var.set("Minutes")
OptionMenu(frame, time_unit_var, "Minutes", "Seconds").grid(row=4, column=0, padx=10, pady=10)

def update_idle_time_plus():
    delta_seconds = 60 if time_unit_var.get() == "Minutes" else 1
    update_idle_time(delta_seconds)

def update_idle_time_minus():
    delta_seconds = -60 if time_unit_var.get() == "Minutes" else -1
    update_idle_time(delta_seconds)

Button(frame, text="-", command=update_idle_time_minus, repeatdelay=400, repeatinterval=100).grid(row=4, column=1, padx=10, pady=10)
Button(frame, text="+", command=update_idle_time_plus, repeatdelay=400, repeatinterval=100).grid(row=4, column=2, padx=10, pady=10)

Button(frame, text="Start", command=start_thread).grid(row=2, column=0, padx=20, pady=10)
Button(frame, text="Stop", command=stop_thread).grid(row=2, column=1, padx=20, pady=10)

q = None
thread = None

root.mainloop()
