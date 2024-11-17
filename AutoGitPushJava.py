import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time


def read_config():
    config_file = "config.txt"
    config_data = {"folder_path": None, "lines_threshold": 3}  # Default threshold is 3

    if not os.path.exists(config_file):
        print(f"Error: '{config_file}' does not exist. Please create it with 'folder_path' and 'lines_threshold'.")
        return None

    with open(config_file, "r") as file:
        for line in file:
            if line.startswith("folder_path="):
                config_data["folder_path"] = line.split("=", 1)[1].strip()
            elif line.startswith("lines_threshold="):
                try:
                    config_data["lines_threshold"] = int(line.split("=", 1)[1].strip())
                except ValueError:
                    print("Error: 'lines_threshold' must be an integer. Using default value (3).")

    if not config_data["folder_path"]:
        print("Error: 'folder_path' not found in config.txt.")
        return None

    return config_data


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, folder_path, lines_threshold):
        self.folder_path = folder_path
        self.line_count = 0
        self.lines_threshold = lines_threshold

    def on_modified(self, event):
        if event.src_path.endswith(".java"):
            print(f"Detected changes in: {event.src_path}")
            self.line_count += 1

            # Trigger commit after reaching the threshold
            if self.line_count >= self.lines_threshold:
                print(f"Triggering auto-commit after {self.lines_threshold} lines of changes...")
                self.commit_to_github()
                self.line_count = 0

    def commit_to_github(self):
        try:
            # Git commands
            subprocess.run(["git", "add", "."], cwd=self.folder_path, check=True)
            subprocess.run(["git", "commit", "-m", f"Auto-commit after {self.lines_threshold} lines of code changes"],
                           cwd=self.folder_path, check=True)
            subprocess.run(["git", "push"], cwd=self.folder_path, check=True)
            print("Changes successfully pushed to GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Error during Git operations: {e}")


def main():
    config_data = read_config()
    if not config_data or not os.path.exists(config_data["folder_path"]):
        print(f"Error: The folder path '{config_data.get('folder_path', '')}' does not exist. Please check config.txt.")
        return

    folder_path = config_data["folder_path"]
    lines_threshold = config_data["lines_threshold"]

    print(f"Monitoring folder: {folder_path}")
    print(f"Will commit changes after every {lines_threshold} lines of code.")

    event_handler = ChangeHandler(folder_path, lines_threshold)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=True)

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping observer...")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
