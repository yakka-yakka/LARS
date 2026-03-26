import os
import time
import subprocess
import threading

from src.state import state, BASE_DIR

AHK_EXE = BASE_DIR / "ahk_env" / "AutoHotkey64.exe"
afk_thread = None

def afk_worker():
    while state.afk_active:
        app_path = str(AHK_EXE)
        script_path = str(BASE_DIR / "scripts" / "afk_sequence.ahk")
        if os.path.exists(app_path) and os.path.exists(script_path):
            subprocess.run([app_path, script_path])
        
        # Wait approx 30 seconds
        for _ in range(30):
            if not state.afk_active:
                break
            time.sleep(1)

def toggle_afk():
    state.afk_active = not state.afk_active
    state.update_ui_signal.emit()
    global afk_thread
    if state.afk_active:
        afk_thread = threading.Thread(target=afk_worker, daemon=True)
        afk_thread.start()

def execute_sync():
    """ Runs the drag operation for all items sequentially """
    for name, coords in state.sync_items.items():
        if state.is_recording:
            break
        subprocess.run([
            str(AHK_EXE), str(BASE_DIR / "scripts" / "drag.ahk"),
            str(coords[0]), str(coords[1]), str(coords[2]), str(coords[3])
        ])
        time.sleep(0.4)

def run_capture_flow():
    """ Spawns AHK capture script, reads stdout, and signals Qt for input box """
    state.is_recording = True
    state.update_ui_signal.emit()
    
    try:
        res = subprocess.run([str(AHK_EXE), str(BASE_DIR / "scripts" / "capture.ahk")], 
                             capture_output=True, text=True, timeout=30)
        out = res.stdout.strip()
        if out:
            parts = [int(p) for p in out.split(",")]
            if len(parts) == 4:
                # Trigger the main thread to show dialog
                state.show_input_signal.emit(parts)
            else:
                state.is_recording = False
                state.update_ui_signal.emit()
        else:
            state.is_recording = False
            state.update_ui_signal.emit()
    except subprocess.TimeoutExpired:
        state.is_recording = False
        state.update_ui_signal.emit()
