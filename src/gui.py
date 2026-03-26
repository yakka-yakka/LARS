import os
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.state import state, BASE_DIR

class HUDOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setGeometry(30, 30, 260, 280)
        
        self.frame = QFrame(self)
        self.frame.setObjectName("mainFrame")
        bg_path = (BASE_DIR / "static" / "backsplash.png").as_posix()
        
        # Universal backdrop layer for all interior text elements
        label_backdrop = "QLabel { background-color: rgba(0, 0, 0, 160); border-radius: 4px; padding: 2px; }"
        
        if os.path.exists(bg_path):
            self.frame.setStyleSheet(f"#mainFrame {{ border-image: url('{bg_path}'); border-radius: 8px; }} " + label_backdrop)
        else:
            self.frame.setStyleSheet(f"#mainFrame {{ background-color: rgba(18, 18, 18, 220); border-radius: 8px; }} " + label_backdrop)
        self.frame.resize(260, 280)
        
        self.layout = QVBoxLayout(self.frame)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        self.lbl_header = QLabel("LARS")
        self.lbl_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.lbl_header.setStyleSheet("color: #00FF00;")
        self.lbl_header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_header)
        
        self.layout.addSpacing(10)
        
        # Profile Section
        self.lbl_profile = QLabel("PROFILE: Default [F11]")
        self.lbl_profile.setFont(QFont("Segoe UI", 9, QFont.Bold))
        self.lbl_profile.setStyleSheet("color: #FFA500;") # Orange
        self.layout.addWidget(self.lbl_profile)
        
        # Loadout Section
        self.lbl_loadout_title = QLabel("▶ LOADOUT SYNC (F9)")
        self.lbl_loadout_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_loadout_title.setStyleSheet("color: #FFFFFF;")
        self.layout.addWidget(self.lbl_loadout_title)
        
        self.lbl_loadout_items = QLabel("No items recorded.")
        self.lbl_loadout_items.setFont(QFont("Segoe UI", 9))
        self.lbl_loadout_items.setStyleSheet("color: #CCCCCC;")
        self.layout.addWidget(self.lbl_loadout_items)
        
        self.layout.addSpacing(10)
        
        # Anti-AFK Section
        self.lbl_afk_title = QLabel("▶ ANTI-AFK MODE (F10)")
        self.lbl_afk_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_afk_title.setStyleSheet("color: #FFFFFF;")
        self.layout.addWidget(self.lbl_afk_title)
        
        self.lbl_afk_status = QLabel("STATUS: OFFLINE")
        self.lbl_afk_status.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.lbl_afk_status.setStyleSheet("color: #FF4444;")
        self.layout.addWidget(self.lbl_afk_status)
        
        self.layout.addStretch()
        
        # Footer
        self.lbl_footer = QLabel("F11: Profile | F9: Sync | F10: AFK")
        self.lbl_footer.setFont(QFont("Segoe UI", 8))
        self.lbl_footer.setStyleSheet("color: #FFFFFF;")
        self.lbl_footer.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_footer)
        
        state.update_ui_signal.connect(self.update_ui)
        state.show_input_signal.connect(self.prompt_save)
        self.update_ui()
        
    def prompt_save(self, coords_list):
        dialog = QInputDialog()
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        
        text, ok = dialog.getText(None, "Record Item", "Name for this mapping:")
        if ok and text:
            state.sync_items[text] = tuple(coords_list)
            state.save_ini()
        
        state.is_recording = False
        self.update_ui()
        
    def update_ui(self):
        curr_section = state.profiles[state.current_profile_idx]
        self.lbl_profile.setText(f"PROFILE: {curr_section} [F11]")
        
        if state.is_recording:
            self.lbl_loadout_items.setText("[RECORDING MODE ACTIVE]")
            self.lbl_loadout_items.setStyleSheet("color: #FFFF00;")
        else:
            if not state.sync_items:
                self.lbl_loadout_items.setText("No items recorded.")
            else:
                items_str = "\n".join([f"• {k}" for k in state.sync_items.keys()])
                self.lbl_loadout_items.setText(items_str)
            self.lbl_loadout_items.setStyleSheet("color: #CCCCCC;")
            
        if state.afk_active:
            self.lbl_afk_status.setText("STATUS: ACTIVE")
            self.lbl_afk_status.setStyleSheet("color: #00FF00;")
        else:
            self.lbl_afk_status.setText("STATUS: OFFLINE")
            self.lbl_afk_status.setStyleSheet("color: #FF4444;")
            
        if state.hud_visible:
            self.show()
        else:
            self.hide()
