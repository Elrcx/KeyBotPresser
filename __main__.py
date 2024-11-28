import os
import keyboard
import time
import json
import threading
from math import ceil
import colors
import queue


CONFIG_DIRECTORY = "configs"
FILES_PER_PAGE = 9
TITLE_MESSAGE = f"{colors.FORE_YELLOW}Press 'Home' to start, 'End' to stop, 'Insert' to select a configuration, or 'Page Up' to toggle looping.{colors.RESET}"

stop_event = threading.Event()
key_event_queue = queue.Queue()
running = False


def key_listener():
    """
    Listens for keypresses and places them in a queue.
    """
    pressed_keys = set()
    def handle_key(event):
        if event.event_type == "down" and event.name not in pressed_keys:
            key_event_queue.put(event.name)
            pressed_keys.add(event.name)
        elif event.event_type == "up" and event.name in pressed_keys:
            pressed_keys.remove(event.name)
    keyboard.hook(handle_key)


def load_config(filename):
    """
    Loads the action queue configuration from the config.json file.
    """
    file_location = os.path.join(CONFIG_DIRECTORY, filename)
    try:
        with open(f"{file_location}", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"{colors.FORE_RED}Error: {file_location} file not found.{colors.RESET}")
        return None
    except json.JSONDecodeError:
        print(f"{colors.FORE_RED}Error: Decoding {filename} failed (wrong JSON format).{colors.RESET}")
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
        print(f"Page {page}/{total_pages}:")
        for i, file in enumerate(current_files, start=1):
            print(f"\t{colors.FORE_GREEN}{i}{colors.RESET}. {file}")

        if total_pages > 1:
            print(f"{colors.FORE_GREEN}[-]{colors.RESET} Previous Page  {colors.FORE_GREEN}[+]{colors.RESET} Next Page")
        print(f"{colors.FORE_GREEN}[Delete]{colors.RESET} Go Back")
        print("*----------------------------------------------------*\n")
        return current_files, total_pages
    except FileNotFoundError:
        print(f"{colors.FORE_RED}Error: Directory {CONFIG_DIRECTORY} not found.{colors.RESET}")
        return [], 1


def select_file():
    """
    Handles file selection and pagination for configuration files.
    """
    page = 1
    files, total_pages = list_files(page)
    while True:
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
                files, total_pages = list_files(page)
            elif event.name == "+":
                if page < total_pages:
                    page += 1
                files, total_pages = list_files(page)
            elif event.name == "delete":
                print("Going back to waiting state without loading.")
                return None


def perform_actions(actions, looping):
    """
    Performs the configured actions from the action queue.
    """
    while running:  # Continue running until `running` is set to False
        for action in actions:
            if not running:
                break
            keys = action.get("key", [])
            press_duration = action.get("duration", 0.1)
            release_delay = action.get("delay", 0.0)
            wait_time = action.get("wait_time", 0.0)
            tag = action.get("tag", "")

            if not keys:
                print("Skipping action with no keys specified.")
                continue

            delay_text = f" (delay {colors.FORE_GREEN}{release_delay}s{colors.RESET})" if release_delay > 0.0 else ""
            tag = "" if tag == "" else f" {colors.FORE_BLUE}{colors.BACK_WHITE} {tag} {colors.RESET}"
            print(f"Pressing {colors.FORE_GREEN}{keys}{colors.RESET} for {colors.FORE_GREEN}{press_duration}s{colors.RESET} and waiting {colors.FORE_GREEN}{wait_time}s{colors.RESET}.{delay_text}{tag}")
            for key in keys:
                keyboard.press(key)
            time.sleep(press_duration)
            for key in keys:
                keyboard.release(key)
                time.sleep(release_delay)
            time.sleep(wait_time)

        if looping and running:
            print(f"{colors.FORE_YELLOW}Loop completed, starting again...{colors.RESET}")
        else:
            break

    if running:
        print(f"{colors.FORE_YELLOW}All actions have been performed. Press 'End' to go back.{colors.RESET}")



def monitor_keys():
    """
    Handles starting and stopping actions from the action queue and allows file selection.
    Processes key events from the queue.
    """
    global running
    threading.Thread(target=key_listener, daemon=True).start()
    print(f"Program is running in the background.")
    actions = None
    looping = False

    while actions is None:
        print(f"{colors.FORE_YELLOW}No configuration loaded. Please select a file.{colors.RESET}")
        selected_file = select_file()
        if selected_file:
            actions = load_config(selected_file)
        else:
            print(f"{colors.FORE_RED}No file selected. Waiting for user input.{colors.RESET}")

    print(f"{TITLE_MESSAGE}")

    while True:
        if not key_event_queue.empty():
            key = key_event_queue.get()
            if key == "home" and not running:
                print("Home key pressed. Starting action queue.")
                running = True
                stop_event.clear()
                threading.Thread(target=perform_actions, args=(actions, looping,), daemon=True).start()
            elif key == "end" and running:
                print(f"End key pressed. Stopping action queue.\n{TITLE_MESSAGE}")
                stop_event.set()
                running = False
            elif key == "insert" and not running:
                print("Insert key pressed. Opening file selection.")
                selected_file = select_file()
                if selected_file:
                    actions = load_config(selected_file)
                    if actions is not None:
                        print(f"Loaded configuration from {selected_file}.\n{TITLE_MESSAGE}")
                else:
                    print(f"No file loaded. Returning to waiting state.\n{TITLE_MESSAGE}")
            elif key == "page up" and not running:
                looping = not looping
                print(f"Looping set to: {looping}")


if __name__ == "__main__":
    # Run key monitoring in separate thread to allow execution in background.
    threading.Thread(target=monitor_keys, daemon=True).start()

    while True:
        time.sleep(1)
