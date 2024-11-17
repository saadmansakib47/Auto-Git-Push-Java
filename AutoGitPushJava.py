import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import time


def read_config():
    config_file = "config.txt"
    if not os.path.exists(config_file):
        print(f"Error: '{config_file}' does not exist. Please create it with the folder_path key.")
        return None

    with open(config_file, "r") as file:
        for line in file:
            if line.startswith("folder_path="):
                return line.split("=", 1)[1].strip()

    print("Error: 'folder_path' not found in config.txt.")
    return None


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.line_count = 0

    def on_modified(self, event):
        if event.src_path.endswith(".java"):
            print(f"Detected changes in: {event.src_path}")
            self.line_count += 1

            if self.line_count >= 3:
                print("Triggering auto-commit...")
                self.commit_to_github()
                self.line_count = 0

    def commit_to_github(self):
        try:
            subprocess.run(["git", "add", "."], cwd=self.folder_path, check=True)
            subprocess.run(["git", "commit", "-m", "Auto-commit after 3 lines of code changes"], cwd=self.folder_path,
                           check=True)
            subprocess.run(["git", "push"], cwd=self.folder_path, check=True)
            print("Changes successfully pushed to GitHub.")
        except subprocess.CalledProcessError as e:
            print(f"Error during Git operations: {e}")


def main():
    folder_path = read_config()
    if not folder_path or not os.path.exists(folder_path):
        print(f"Error: The folder path '{folder_path}' does not exist. Please check config.txt.")
        return

    print(f"Monitoring folder: {folder_path}")
    event_handler = ChangeHandler(folder_path)
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
