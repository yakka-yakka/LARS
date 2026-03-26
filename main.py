import sys
import os
import time
import ctypes
import threading
from pathlib import Path

# Important: Fix for PyQt5 not finding its own plugins sometimes in embedded distributions
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(Path(__file__).parent.resolve() / "python_env" / "Lib" / "site-packages" / "PyQt5" / "Qt5" / "plugins" / "platforms")

# Enforce Single Instance
MUTEX_NAME = "Global\\LARS_MainProcess"
mutex = ctypes.windll.kernel32.CreateMutexW(None, False, MUTEX_NAME)
if ctypes.windll.kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
    sys.exit(0)

BASE_DIR = Path(__file__).parent.resolve()
sys.path.append(str(BASE_DIR))

from pynput import keyboard
from PyQt5.QtWidgets import QApplication

# Core Sub-Modules
from src.state import state
from src.gui import HUDOverlay
from src.actions import toggle_afk, execute_sync, run_capture_flow

# --- Listener State ---
ctrl_pressed = False
f9_press_time = 0

def on_press(key):
    global ctrl_pressed, f9_press_time
    if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
        ctrl_pressed = True
        
    if key == keyboard.Key.f11:
        if not state.is_recording:
            state.cycle_profile()
            
    if key == keyboard.Key.f10:
        if not state.is_recording:
            toggle_afk()
            
    if key == keyboard.Key.f9:
        if state.is_recording:
            return
            
        if ctrl_pressed:
            state.hud_visible = not state.hud_visible
            state.update_ui_signal.emit()
        else:
            if f9_press_time == 0:
                f9_press_time = time.time()

def on_release(key):
    global ctrl_pressed, f9_press_time
    if key in [keyboard.Key.ctrl_l, keyboard.Key.ctrl_r]:
        ctrl_pressed = False
        
    if key == keyboard.Key.f9:
        if state.is_recording:
            return
            
        if f9_press_time > 0 and not ctrl_pressed:
            duration = time.time() - f9_press_time
            f9_press_time = 0
            
            if duration > 0.4:
                threading.Thread(target=run_capture_flow, daemon=True).start()
            else:
                threading.Thread(target=execute_sync, daemon=True).start()


# --- Main Application Loop ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Needs to stay alive
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    hud = HUDOverlay()
    hud.show()
    
    sys.exit(app.exec_())
