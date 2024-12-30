import os
import pyautogui
import time
import threading
import tkinter as tk
from tkinter import filedialog, simpledialog

def get_directory_path():
    root = tk.Tk()
    root.withdraw()
    directory_path = filedialog.askdirectory(title="Choose the buttons images folder directory")
    return directory_path

def find_and_click(image_path, confidence=0.7):
    try:
        button_location = pyautogui.locateCenterOnScreen(image_path, confidence=confidence)
        if button_location:
            print(f"The answer button has been found : {button_location}")
            pyautogui.click(button_location)
            return True
        else:
            print("The answer button not found !")
            return False
    except Exception as e:
        print(f"Waiting for video call... {e}")
        return False

def start_countdown_gui(call_duration, stop_event):

    def update_timer():
        nonlocal remaining_time
        if remaining_time > 0 and not stop_event.is_set():
            minutes, seconds = divmod(remaining_time, 60)
            timer_label.config(text=f"{minutes:02}:{seconds:02}")
            remaining_time -= 1
            root.after(1000, update_timer)
        else:
            root.destroy()  

    root = tk.Tk()
    root.title("Call Duration")
    root.geometry("200x100")

    timer_label = tk.Label(root, text="", font=("Helvetica", 24), fg="red")
    timer_label.pack(expand=True)

    remaining_time = call_duration
    update_timer()

    root.mainloop()

def monitor_and_manage_call(call_duration, answer_button_paths, end_button_path):
    while True:
        print("\nWatchig over video call...")

        call_answered = False
        call_start_time = None
        stop_event = threading.Event()

        while True:
            if call_answered:
                elapsed_time = time.time() - call_start_time
                print(f"Time passed in seconds : {elapsed_time:.2f}")

                if elapsed_time >= (call_duration - 2):
                    print(f"\nAttempt to stop video call.")

                    pyautogui.press(['tab'])
                    pyautogui.press(['tab'])
                    time.sleep(1)

                    if find_and_click(end_button_path):
                        print("Video call has stopped.")
                        stop_event.set()
                        break
                    else:
                        print("Answer button not found.")


                for path in answer_button_paths:
                    if find_and_click(path):
                        time.sleep(2)
                        print(f"{path} has been clicked!")
                        call_answered = True
                        call_start_time = time.time()

            else:
                for path in answer_button_paths:
                    if find_and_click(path):
                        time.sleep(2)
                        print(f"{path} has been clicked!")
                        call_answered = True
                        call_start_time = time.time()
                        
                        threading.Thread(target=start_countdown_gui, args=(call_duration - 2, stop_event)).start()


            time.sleep(1)

if __name__ == "__main__":
    if not os.path.exists("config.txt"):
        dir_path = get_directory_path()
        with open('config.txt', 'w') as config_file:
            config_file.write(f"{dir_path}\n")
        print(f"Directory saved: {dir_path}")
    else:
        with open('config.txt', 'r') as config_file:
            dir_path = config_file.readline().strip()
        print(f"Using existing directory: {dir_path}")

    answer_button_image = os.path.join(dir_path, "answer_button.png")
    end_button_image = os.path.join(dir_path, "end_button.png")
    answer_button_opt_image = os.path.join(dir_path, "answer_button_opt.png")
    answer_images = [answer_button_image, answer_button_opt_image]

    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    call_duration_in_seconds = simpledialog.askinteger("Duration Input", "Insert the call duration :")

    monitor_and_manage_call(call_duration_in_seconds, answer_images, end_button_image)