import Quartz
import time
import threading
import pyautogui
import queue
from tkinter import Tk, StringVar, Button, OptionMenu
from tkinter.ttk import Label, Frame, Style
from pynput import mouse

SECONDS_PER_MINUTE = 60
DEFAULT_IDLE_TIME = 4 * SECONDS_PER_MINUTE  # 4 minutes

class IdleTimeController:
    def __init__(self, root):
        self.root = root
        self.idle_time = DEFAULT_IDLE_TIME  # Setting default idle time to 4 minutes
        self.movement_label_text = StringVar()
        self.idle_time_var = StringVar()
        self.setup_ui()
        self.q = None
        self.thread = None

    def get_last_activity_time(self):
        return time.time()

    def is_system_idle(self, last_activity_time):
        return (time.time() - last_activity_time) >= self.idle_time

    def move_cursor(self):
        last_activity_time = self.get_last_activity_time()

        def on_move(x, y):
            nonlocal last_activity_time
            last_activity_time = self.get_last_activity_time()

        def on_click(x, y, button, pressed):
            nonlocal last_activity_time
            last_activity_time = self.get_last_activity_time()

        def on_scroll(x, y, dx, dy):
            nonlocal last_activity_time
            last_activity_time = self.get_last_activity_time()

        with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
            while True:
                try:
                    self.q.get_nowait()
                    break
                except queue.Empty:
                    pass

                if self.is_system_idle(last_activity_time):
                    try:
                        pyautogui.moveRel(10, 10, duration=0.25)
                        pyautogui.moveRel(-10, -10, duration=0.25)
                    except pyautogui.FailSafeException:
                        self.handle_failsafe()

                    last_activity_time = self.get_last_activity_time()

                time.sleep(2)

    def handle_failsafe(self):
        screen_width, screen_height = pyautogui.size()
        pyautogui.FAILSAFE = False
        pyautogui.moveTo(screen_width / 2, screen_height / 2)
        pyautogui.FAILSAFE = True
        print("Fail-safe triggered. Moving cursor to the center of the screen.")

    def start_thread(self):
        self.q = queue.Queue()
        self.thread = threading.Thread(target=self.move_cursor)
        self.thread.start()

    def stop_thread(self):
        if self.thread:
            self.q.put(True)
            self.thread.join()

    def update_idle_time(self, delta_seconds):
        self.idle_time = max(0, self.idle_time + delta_seconds)
        self.update_labels()

    def setup_ui(self):
        self.root.title("Magic Mouse")
        self.root.geometry("450x250")

        style = Style()
        style.configure("TButton", font=("Arial", 12), padding=10)
        style.configure("TLabel", font=("Arial", 12))

        frame = Frame(self.root, padding="10 10 10 10")
        frame.pack(fill="both", expand=True)

        self.update_labels()
        Label(frame, textvariable=self.movement_label_text).grid(row=0, column=0, columnspan=4, pady=10)
        Label(frame, textvariable=self.idle_time_var).grid(row=3, column=0, padx=10, pady=10)

        self.time_unit_var = StringVar(value="Minutes")
        OptionMenu(frame, self.time_unit_var, "Minutes", "Seconds").grid(row=4, column=0, padx=10, pady=10)

        Button(frame, text="-", command=lambda: self.update_idle_time(-SECONDS_PER_MINUTE if self.time_unit_var.get() == "Minutes" else -1), repeatdelay=400, repeatinterval=100).grid(row=4, column=1, padx=10, pady=10)
        Button(frame, text="+", command=lambda: self.update_idle_time(SECONDS_PER_MINUTE if self.time_unit_var.get() == "Minutes" else 1), repeatdelay=400, repeatinterval=100).grid(row=4, column=2, padx=10, pady=10)

        Button(frame, text="Start", command=self.start_thread).grid(row=2, column=0, padx=20, pady=10)
        Button(frame, text="Stop", command=self.stop_thread).grid(row=2, column=1, padx=20, pady=10)

    def update_labels(self):
        minutes, seconds = divmod(self.idle_time, SECONDS_PER_MINUTE)
        self.movement_label_text.set(f"Intermittent movement after {minutes} minutes {seconds} seconds of inactivity")
        self.idle_time_var.set(f"Idle Time: {minutes} minutes {seconds} seconds")

if __name__ == "__main__":
    root = Tk()
    controller = IdleTimeController(root)
    root.mainloop()
