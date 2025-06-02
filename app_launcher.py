import webview
import threading
import subprocess
import time
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource (for PyInstaller) """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def run_streamlit():
    app_path = resource_path("app.py")
    subprocess.Popen(["streamlit", "run", app_path, "--server.port=8501"])
    time.sleep(2)

if __name__ == '__main__':
    threading.Thread(target=run_streamlit).start()
    webview.create_window("SROI Calculator", "http://localhost:8501")
    webview.start()



