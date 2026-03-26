import configparser
from pathlib import Path
from PyQt5.QtCore import pyqtSignal, QObject

BASE_DIR = Path(__file__).parent.parent.resolve()
INI_FILE = BASE_DIR / "settings.ini"

class AppState(QObject):
    update_ui_signal = pyqtSignal()
    show_input_signal = pyqtSignal(list)
    show_error_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.afk_active = False
        self.sync_items = {} # key -> (startX, startY, endX, endY)
        self.is_recording = False
        self.hud_visible = True
        
        self.profiles = ["Default"]
        self.current_profile_idx = 0
        self.config = configparser.ConfigParser()
        self.config.optionxform = str # preserve case
        
        self.load_ini()
        
    def load_ini(self):
        if INI_FILE.exists():
            self.config.read(INI_FILE)
            sections = self.config.sections()
            
            # Migrate legacy '[Coordinates]' section to '[Default]' automatically
            if "Coordinates" in sections:
                if "Default" not in sections:
                    self.config.add_section("Default")
                for k, v in self.config.items("Coordinates"):
                    self.config.set("Default", k, v)
                self.config.remove_section("Coordinates")
                with open(INI_FILE, "w") as f:
                    self.config.write(f)
                sections = self.config.sections()
                
            if sections:
                self.profiles = sections
                
        if not self.profiles:
            self.profiles = ["Default"]
            
        if self.current_profile_idx >= len(self.profiles):
            self.current_profile_idx = 0
            
        curr_section = self.profiles[self.current_profile_idx]
        if not self.config.has_section(curr_section):
            self.config.add_section(curr_section)
            
        self.sync_items = {}
        for name, coords in self.config.items(curr_section):
            try:
                parts = [int(p.strip()) for p in coords.split(",") if p.strip()]
                if len(parts) >= 4:
                    self.sync_items[name] = tuple(parts[:4])
            except Exception:
                pass
                    
    def save_ini(self):
        curr_section = self.profiles[self.current_profile_idx]
        if not self.config.has_section(curr_section):
            self.config.add_section(curr_section)
            
        # Clear section before saving to purge deleted items
        self.config.remove_section(curr_section)
        self.config.add_section(curr_section)
        
        for name, coords in self.sync_items.items():
            self.config.set(curr_section, name, f"{coords[0]}, {coords[1]}, {coords[2]}, {coords[3]}")
            
        with open(INI_FILE, "w") as f:
            self.config.write(f)
            
    def cycle_profile(self):
        self.current_profile_idx = (self.current_profile_idx + 1) % len(self.profiles)
        self.load_ini()
        self.update_ui_signal.emit()

# Global Singleton State
state = AppState()
