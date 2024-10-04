import json
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QShortcut, QComboBox, QSizePolicy, QMenu, QPushButton, QVBoxLayout, QHBoxLayout, QScrollArea, QLineEdit, QFileDialog
from PyQt5.QtGui import QKeySequence
from gui import util
from gui.colortheme import CustomColorTheme
from data_structure.skillunit import ActionUnit

class HotkeyItem(QPushButton):
    def __init__(self, name, sequence):
        super().__init__()
        self.name = name
        self.sequence = sequence
        self.setCursor(Qt.PointingHandCursor)
        color = ActionUnit.gen_hex_color(name)
        self.setStyleSheet(f'''
            QWidget {{
                background-color: {color};
            }}
            
            QWidget:hover {{
                background-color: {util.lighten_hex_color(color,.2)};
                border: 1px solid white;
            }}''')
        
        self.name = QLabel(f"{name} ({sequence})")
        self.name.setStyleSheet(f"{CustomColorTheme.BOLD_FONT_2} padding: 2px;")   
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.addWidget(self.name)
        
class NameHotkeys(QWidget):
    SetName = pyqtSignal(str)
    def __init__(self, width):
        super().__init__()
        self.valid_keys = self.get_valid_key_codes()
        
        self.name_to_shortcut_dict = {}
        self.name_to_hotkey_dict = {}
        self.name_to_item_dict = {}
        self.menu = QMenu()
        
        self.setContentsMargins(0,0,0,0)
        
        self.item_height = 30
        self.item_width = width
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        
        # self.create_item("TestName","N")
        # self.create_item("move_to","O")
        
    def get_valid_key_codes(self):
        """ Return a set of valid Qt key codes by reflecting over Qt constants. """
        valid_keys = set()
        for attr_name in dir(Qt):
            if attr_name.startswith('Key_'):
                try:
                    key_code = getattr(Qt, attr_name)
                    valid_keys.add(key_code)
                except AttributeError:
                    continue
        return valid_keys

    def clear_hotkeys(self):
        hotkey_names = list(self.name_to_shortcut_dict.keys())
        for name in hotkey_names:
            del self.name_to_shortcut_dict[name]
            delete_hotkey = self.name_to_hotkey_dict.pop(name)
            delete_hotkey.deleteLater()
            delete_item = self.name_to_item_dict.pop(name)
            self.layout.removeWidget(delete_item)
            delete_item.deleteLater()
    
    def create_item(self, name, sequence):
        key_parts = sequence.split("+")
        for key_part in key_parts:
            if hasattr(Qt, f'Key_{key_part}'):
                key_code = getattr(Qt, f'Key_{key_part}')
                if key_code not in self.valid_keys:
                    return False
            else:
                return False
            
        # Swap out existing item if it exists
        if sequence in self.name_to_shortcut_dict.values():
            curr_name = [key for key, value in self.name_to_shortcut_dict.items() if value == sequence][0]
            del self.name_to_shortcut_dict[curr_name]
            delete_hotkey = self.name_to_hotkey_dict.pop(curr_name)
            delete_hotkey.deleteLater()
            delete_item = self.name_to_item_dict.pop(curr_name)
            self.layout.removeWidget(delete_item)
            delete_item.deleteLater()
        # Replace existing item if it exists
        if name in self.name_to_hotkey_dict:
            del self.name_to_shortcut_dict[name]
            delete_hotkey = self.name_to_hotkey_dict.pop(name)
            delete_hotkey.deleteLater()
            delete_item = self.name_to_item_dict.pop(name)
            self.layout.removeWidget(delete_item)
            delete_item.deleteLater()
            
        hotkey = QShortcut(QKeySequence(sequence), self)
        emit_name_lambda = lambda: self.emit_name(name)
        hotkey.activated.connect(emit_name_lambda)
        self.name_to_hotkey_dict[name] = hotkey
        self.name_to_shortcut_dict[name] = sequence
        
        item = HotkeyItem(name,sequence)
        item.clicked.connect(emit_name_lambda)
        item.setFixedHeight(self.item_height)
        item.setFixedWidth(self.item_width)
        self.name_to_item_dict[name] = item
        self.layout.addWidget(item)
        self.update_items()
        return True
        
    def update_items(self):
        num_children = self.layout.count()*self.item_height
        self.setFixedHeight(num_children)
        self.setFixedWidth(self.item_width)
        self.update()
    
    def delete_item(self, name):
        item = self.name_to_item_dict.pop(name)
        hotkey = self.name_to_hotkey_dict.pop(name)
        self.layout.removeWidget(item)
        item.deleteLater()
        hotkey.deleteLater()
    
    def emit_name(self, name):
        print(f"Emitting {name}")
        self.SetName.emit(name)
        pass

class HotkeyBar(QWidget):
    def __init__(self):
        super().__init__()
        width = 250
        self.setAutoFillBackground(True)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setObjectName("HotkeyBar")
        self.setStyleSheet(f"#{self.objectName()} {{background-color: {CustomColorTheme.ACCENT_1};}}")
        self.setContentsMargins(0,0,0,0)
        self.setFixedWidth(width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        self.skill_sidebar = NameHotkeys(width)

        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0,0,0,0)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(CustomColorTheme.get_scroll_accent_style("QScrollArea"))
        self.scroll_area.setWidget(self.skill_sidebar)
        self.scroll_area.setAttribute(Qt.WA_StyledBackground) 
        
        self.add_button = QPushButton("Add Name Hotkey")
        self.add_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.add_button.setCursor(Qt.PointingHandCursor)
        self.add_button.clicked.connect(self.add_name_hotkey)
        
        self.enter_behavior_name = QLineEdit("Behavior Name")
        self.enter_behavior_name.setStyleSheet(CustomColorTheme.MONO_FONT_2)
        self.enter_sequence = QComboBox()
        self.enter_sequence.setStyleSheet(CustomColorTheme.FONT_2)
        self.enter_sequence.setCursor(Qt.PointingHandCursor)
        self.keylist = ["1","2","3","4","5","6","7","8","9","0","Shift+1","Shift+2","Shift+3","Shift+4","Shift+5","Shift+6","Shift+7","Shift+8","Shift+9","Shift+0"]
        self.enter_sequence.addItems(self.keylist)

        self.import_button = QPushButton("Import")
        self.import_button.clicked.connect(self.import_hotkeys)
        self.import_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.import_button.setCursor(Qt.PointingHandCursor)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_hotkeys)
        self.export_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.export_button.setCursor(Qt.PointingHandCursor)
        
        
        self.minilayout = QHBoxLayout()
        self.minilayout.setContentsMargins(10,5,10,5)
        self.minilayout.setSpacing(10)
        self.minilayout.addWidget(self.import_button)
        self.minilayout.addWidget(self.export_button)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.layout.addLayout(self.minilayout)
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.enter_behavior_name)
        self.layout.addWidget(self.enter_sequence)
        self.layout.addWidget(self.add_button)
    
    def export_hotkeys(self):
        filename, _ = QFileDialog.getSaveFileName(
                None,
                "Save File",
                "",
                "JSON Files (*.json)"
            )
        if filename:
            if not filename.lower().endswith('.json'):
                filename += '.json'
                
            with open(filename, 'w') as file:
                json.dump(self.skill_sidebar.name_to_shortcut_dict, file)
                
            print(f"File will be saved as: {filename}")
    
    def import_hotkeys(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Hotkey File", "", "JSON Files (*.json)")
        if file_path:
            print("Loading hotkeys from", file_path)
            with open(file_path, 'r') as file:
                try:
                    hotkey_dict = json.load(file)
                    self.skill_sidebar.clear_hotkeys()
                    for name, sequence in hotkey_dict.items():
                        if sequence in self.keylist:
                            self.skill_sidebar.create_item(name, sequence)
                        else:
                            print(f"Invalid sequence {sequence} for {name}. Skipping.")
                    self.update_recommended_hotkeyindex()
                except (json.JSONDecodeError):
                    print("Error decoding JSON file")
    
    def update_recommended_hotkeyindex(self):
        # Find first index in keylist that is not in self.skill_sidebar.name_to_shortcut_dict.values(). If none, default to 0
        first_index = next((i for i,key in enumerate(self.keylist) if key not in self.skill_sidebar.name_to_shortcut_dict.values()), 0)
        self.enter_sequence.setCurrentIndex(first_index)
    
    def add_name_hotkey(self):
        name = self.enter_behavior_name.text()
        sequence = self.enter_sequence.currentText()
        
        self.skill_sidebar.create_item(name, sequence)
        self.update_recommended_hotkeyindex()