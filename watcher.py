import time
import subprocess
import os
import sys
import ctypes
from pathlib import Path

# Enforce Single Instance of the Watcher
MUTEX_NAME = "Global\\LARS_WatcherProcess"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
    sys.exit(0)

BASE_DIR = Path(__file__).parent.resolve()
PYTHON_EXE = BASE_DIR / "python_env" / "pythonw.exe"
MAIN_SCRIPT = BASE_DIR / "main.py"

def find_arma_window():
    """ Uses Win32 C-API to securely extract visible window titles, effortlessly bypassing Anti-Cheat process blocks """
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible

    found_hwnd = None

    def foreach_window(hwnd, lParam):
        nonlocal found_hwnd
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                title = buff.value.lower()
                
                # Check for game title while heavily filtering out obvious false-positives (Web Browsers, IDEs, GitHub strings)
                if "arma reforger" in title:
                    false_positives = ["chrome", "firefox", "edge", "opera", "github", "code", "notepad", "discord", "brave"]
                    if not any(fp in title for fp in false_positives):
                        found_hwnd = hwnd
                        return False  # Stop searching once found
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    return found_hwnd

def main():
    app_process = None
    
    while True:
        try:
            # Continuously check for the physical Arma Reforger window
            arma_hwnd = find_arma_window()
            arma_running = (arma_hwnd is not None)
            
            # Scenario 1: Game running, but our overlay isn't
            if arma_running and app_process is None:
                app_process = subprocess.Popen([str(PYTHON_EXE), str(MAIN_SCRIPT)])
                
            # Scenario 2: Game stopped (window deleted), but our overlay is still running
            elif not arma_running and app_process is not None:
                app_process.kill() # Instantly destroy instead of gracefully terminating
                app_process.wait(timeout=1)
                app_process = None
                
            # Scenario 3: Game running, overlay is running, but overlay crashed
            elif arma_running and app_process is not None:
                if app_process.poll() is not None:
                    app_process = subprocess.Popen([str(PYTHON_EXE), str(MAIN_SCRIPT)])
                    
        except Exception as e:
            pass
            
        # 1-second ticks for incredibly fast response times
        time.sleep(1)

if __name__ == "__main__":
    main()
