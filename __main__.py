import os

import keyboard
import time
import json
import threading


CONFIG_DIRECTORY = "configs"


def load_config(filename):
    """
    Loads the action queue configuration from the config.json file.
    """
    file_location = os.path.join(CONFIG_DIRECTORY, filename)
    try:
        with open(f"{file_location}", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {file_location} file not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Decoding {filename} failed (wrong JSON format).")
        return None


def perform_actions(actions):
    """
    Performs the configured actions from the action queue.
    """
    for action in actions:
        key = action.get("key")
        press_duration = action.get("duration", 0.1)
        wait_time = action.get("wait_time", 0.1)

        if not key:
            print("Skipping action with no key specified.")
            continue

        print(f"Pressing {key} for {press_duration}s and waiting {wait_time}s.")
        keyboard.press(key)
        time.sleep(press_duration)
        keyboard.release(key)
        time.sleep(wait_time)
    print(f"All actions have been performed. Press 'End' to go back.")


def monitor_keys():
    """
    Handles starting and stopping actions from the action queue.
    """
    print("Program is running in the background. Press 'Home' to start and 'End' to stop.")
    running = False
    actions = load_config("config_example.json")

    while True:
        if keyboard.is_pressed("home") and not running:
            print("Home key pressed. Starting action queue.")
            running = True
            perform_actions(actions)
        elif keyboard.is_pressed("end") and running:
            print("End key pressed. Stopping action queue.")
            running = False
            time.sleep(0.5)


if __name__ == "__main__":
    # Run key monitoring in separate thread to allow execution in background.
    threading.Thread(target=monitor_keys, daemon=True).start()

    while True:
        time.sleep(1)
