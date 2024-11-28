import os
import keyboard
import time
import json
import threading
from math import ceil


CONFIG_DIRECTORY = "configs"
FILES_PER_PAGE = 9
TITLE_MESSAGE = "Press 'Home' to start, 'End' to stop, or 'Insert' to select a configuration."


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


def list_files(page=1):
    """
    Lists files in the CONFIG_DIRECTORY with pagination.
    """
    try:
        files = [f for f in os.listdir(CONFIG_DIRECTORY) if os.path.isfile(os.path.join(CONFIG_DIRECTORY, f))]
        total_pages = ceil(len(files) / FILES_PER_PAGE)
        start_idx = (page - 1) * FILES_PER_PAGE
        end_idx = start_idx + FILES_PER_PAGE
        current_files = files[start_idx:end_idx]

        print("\n*----------------------------------------------------*")
        print(f"Page {page}/{total_pages}")
        for i, file in enumerate(current_files, start=1):
            print(f"\t{i}. {file}")

        if total_pages > 1:
            print("[-] Previous Page  [+] Next Page")
        print("[Delete] Go Back")
        print("*----------------------------------------------------*\n")
        return current_files, total_pages
    except FileNotFoundError:
        print(f"Error: Directory {CONFIG_DIRECTORY} not found.")
        return [], 1


def select_file():
    """
    Handles file selection and pagination for configuration files.
    """
    page = 1
    while True:
        files, total_pages = list_files(page)
        event = keyboard.read_event()
        if event.event_type == "down":
            if event.name in map(str, range(1, FILES_PER_PAGE + 1)):
                selected_idx = int(event.name) - 1
                if selected_idx < len(files):
                    selected_file = files[selected_idx]
                    print(f"Selected: {selected_file}")
                    return selected_file
            elif event.name == "-":
                if page > 1:
                    page -= 1
            elif event.name == "+":
                if page < total_pages:
                    page += 1
            elif event.name == "delete":
                print("Going back to waiting state without loading.")
                return None


def perform_actions(actions):
    """
    Performs the configured actions from the action queue.
    """
    for action in actions:
        keys = action.get("key", [])
        press_duration = action.get("duration", 0.1)
        release_delay = action.get("delay", 0.0)
        wait_time = action.get("wait_time", 0.0)

        if not keys:
            print("Skipping action with no keys specified.")
            continue

        delay_text = f" (delay {release_delay})" if release_delay > 0.0 else ""
        print(f"Pressing {keys} for {press_duration}s and waiting {wait_time}s.{delay_text}")
        for key in keys:
            keyboard.press(key)
        time.sleep(press_duration)
        for key in keys:
            keyboard.release(key)
            time.sleep(release_delay)
        time.sleep(wait_time)
    print(f"All actions have been performed. Press 'End' to go back.")



def monitor_keys():
    """
    Handles starting and stopping actions from the action queue and allows file selection.
    """
    print(f"Program is running in the background.")
    running = False
    in_config = False
    actions = None

    while actions is None:
        print("No configuration loaded. Please select a file.")
        selected_file = select_file()
        if selected_file:
            actions = load_config(selected_file)
        else:
            print("No file selected. Waiting for user input.")

    print(f"{TITLE_MESSAGE}")

    while True:
        if keyboard.is_pressed("home") and not running and not in_config:
            print("Home key pressed. Starting action queue.")
            running = True
            perform_actions(actions)
        elif keyboard.is_pressed("end") and running:
            print(f"End key pressed. Stopping action queue.\n{TITLE_MESSAGE}")
            running = False
            time.sleep(0.5)
        elif keyboard.is_pressed("insert") and not running and not in_config:
            print("Insert key pressed. Opening file selection.")
            in_config = True
            selected_file = select_file()
            if selected_file:
                actions = load_config(selected_file)
                in_config = False
                if actions is not None:
                    print(f"Loaded configuration from {selected_file}.\n{TITLE_MESSAGE}")
            else:
                in_config = False
                print(f"No file loaded. Returning to waiting state.\n{TITLE_MESSAGE}")


if __name__ == "__main__":
    # Run key monitoring in separate thread to allow execution in background.
    threading.Thread(target=monitor_keys, daemon=True).start()

    while True:
        time.sleep(1)
