import uuid
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QLabel, QFrame, QSizePolicy, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit
from gui.colortheme import CustomColorTheme

class NaryRangeTreeSkillSegaWrapper():
    def __init__(self, skill_tree):
        self._wrapped_obj = skill_tree
        self.skill_emissions = {} # {uuid: SkillEmission}
    
    def insert(self, value, range_start, range_end, trigger_delete_skill, zoom_selection):
        self._wrapped_obj.insert(value, range_start, range_end)
        skill_uuid = value.uuid
        if skill_uuid not in self.skill_emissions:
            self.skill_emissions[skill_uuid] = SkillEmission(skill_uuid, range_start, range_end)
        self.skill_emissions[skill_uuid].SendDelete.connect(trigger_delete_skill)
        self.skill_emissions[skill_uuid].ZoomSelection.connect(zoom_selection)
        self.skill_emissions[skill_uuid].ToggleShowUnder.connect(self.toggle_show_under)
    
    def toggle_show_under(self, uuid, hideUnder = False):
        print("Toggling show under", uuid, hideUnder)
        lambda_func = lambda x: x.uuid == uuid
        value = self._wrapped_obj.get(lambda_func)
        hide_list = []
        self._wrapped_obj._traverse_recursive(value, hide_list,-1)
        hide_list.pop(0)
        for skill in hide_list:
            print("Hide",hideUnder,skill.value.uuid)
            if hideUnder:
                self.skill_emissions[skill.value.uuid].hide()
            else:
                self.skill_emissions[skill.value.uuid].show()
        print("Done")
    
    def pop(self, value):
        skill = self._wrapped_obj.pop(value)
        print("Successfully popped", skill.value.uuid)
        
        if skill.value.uuid not in self.skill_emissions:
            raise ValueError(f"Skill emission with uuid {skill.value.uuid} not found.")
        skill_emission = self.skill_emissions.pop(skill.value.uuid)
        
        return skill, skill_emission
    
    def connect_sidebar(self, skill_uuid, skill_emission):
        if skill_uuid not in self.skill_emissions:
            AssertionError(f"Skill emission with uuid {skill_uuid} not inserted into tree.")
        self.skill_emissions[skill_uuid].connect_sidebar(skill_emission)
    
    def connect_framewidget(self, skill_uuid, skill_emission):
        if skill_uuid not in self.skill_emissions:
            AssertionError(f"Skill emission with uuid {skill_uuid} not inserted into tree.")
        self.skill_emissions[skill_uuid].connect_framewidget(skill_emission)
    
    def clear(self):
        self._wrapped_obj.clear()
        for skill_emission in self.skill_emissions.values():
            skill_emission.deleteLater()
        self.skill_emissions.clear()
        
    def __getattr__(self, name):
        return getattr(self._wrapped_obj, name)
    
    def dewrap(self):
        return self._wrapped_obj

class SkillEmission(QObject):
    SendDelete = pyqtSignal(uuid.UUID)
    ZoomSelection = pyqtSignal(float,float)
    ToggleShowUnder = pyqtSignal(uuid.UUID, bool)
    def __init__(self, uuid, frame_start, frame_end):
        super().__init__()
        self.uuid = uuid
        self.frame_start = frame_start
        self.frame_end = frame_end
        
    def deleteLater(self):
        self.frame_widget.deleteLater()
        self.sidebar_widget.deleteLater()
        super().deleteLater()
    
    def connect_sidebar(self, sidebar):
        self.sidebar_widget = sidebar
        self.sidebar_widget.HoverSidebar.connect(self.hover_control)
        self.sidebar_widget.delete_button.clicked.connect(self.delete)
        self.sidebar_widget.zoom_button.clicked.connect(self.zoom_selection)
        self.sidebar_widget.nestbutton.toggled.connect(self.toggle_show_under)
    
    def toggle_show_under(self, hideUnder):
        self.ToggleShowUnder.emit(self.uuid, hideUnder)
    
    def connect_framewidget(self, frame_widget):
        self.frame_widget = frame_widget
        self.frame_widget.HoverFrame.connect(self.hover_control)
    
    def hide(self):
        if self.sidebar_widget:
            self.sidebar_widget.hide()
        if self.frame_widget:
            self.frame_widget.hide()
    
    def show(self):
        if self.sidebar_widget:
            self.sidebar_widget.show()
        if self.frame_widget:
            self.frame_widget.show()
    
    def zoom_selection(self):
        self.ZoomSelection.emit(self.frame_start, self.frame_end)
    
    def delete(self):
        print("Deleting skill", self.uuid)
        self.SendDelete.emit(self.uuid)
    
    def hover_control(self, hover):
        if hover:
            if self.sidebar_widget:
                self.sidebar_widget.hover_on()
            if self.frame_widget:
                self.frame_widget.hover_on()
        else:
            if self.sidebar_widget:
                self.sidebar_widget.hover_off()
            if self.frame_widget:
                self.frame_widget.hover_off()
    
class SkillCreator(QWidget):
    EnterSkill = pyqtSignal(str)
    EnterAction = pyqtSignal(str)
    EnterFillAction = pyqtSignal(str)
    EnterQuickAction = pyqtSignal(str)
    SetStart = pyqtSignal()
    SetEnd = pyqtSignal()
    def __init__(self):
        super().__init__()
        
        # Top Bar
        self.top_bar = QHBoxLayout()
        self.top_bar.setAlignment(Qt.AlignCenter)
        self.top_bar.setSpacing(10)
        self.top_bar.setContentsMargins(0,0,0,0)
        # 1st Column
        self.top_column_1 = QVBoxLayout()
        self.top_column_1.setSpacing(5)
        self.top_column_1.setContentsMargins(0,0,0,0)
        
        self.quick_action = QPushButton("Quick Action (Q)")
        self.quick_action.clicked.connect(self.emit_quick_action)
        self.quick_action.setCursor(Qt.PointingHandCursor)
        self.quick_action.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.quick_action.setFixedWidth(150)
        
        self.quick_zoom = QPushButton("Quick Zoom (Z)")
        self.quick_zoom.setCursor(Qt.PointingHandCursor)
        self.quick_zoom.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.quick_zoom.setFixedWidth(150)
        
        self.set_start_button = QPushButton("Set Start (W)")
        self.set_start_button.clicked.connect(self.set_start)
        self.set_start_button.setCursor(Qt.PointingHandCursor)
        self.set_start_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton", CustomColorTheme.PLAY))
        self.set_start_button.setFixedWidth(150)
        
        self.set_end_button = QPushButton("Set End (S)")
        self.set_end_button.clicked.connect(self.set_end)
        self.set_end_button.setCursor(Qt.PointingHandCursor)
        self.set_end_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton", CustomColorTheme.PAUSE))
        self.set_end_button.setFixedWidth(150)
        
        
        self.top_column_1.addWidget(self.quick_action)
        self.top_column_1.addWidget(self.quick_zoom)
        self.top_column_1.addWidget(self.set_start_button)
        self.top_column_1.addWidget(self.set_end_button)
        
        # 2nd Column
        self.top_column_2 = QVBoxLayout()
        self.top_column_2.setSpacing(2)
        self.top_column_2.setContentsMargins(0,0,0,0)
        self.top_column_2.setAlignment(Qt.AlignVCenter)
        self.enter_skill_name_label = QLabel("Current Behavior Name:")
        self.enter_skill_name_label.setStyleSheet(CustomColorTheme.BOLD_FONT_1+"color: white;")
        
        self.enter_skill_name = QLineEdit("Behavior Name")
        self.enter_skill_name.setStyleSheet(CustomColorTheme.MONO_FONT_2)
        self.enter_skill_name.setFixedWidth(250)
        
        self.top_column_2.addWidget(self.enter_skill_name_label)
        self.top_column_2.addWidget(self.enter_skill_name)
        
        # Combine top cols
        self.topColLine = QFrame()
        self.topColLine.setFrameShape(QFrame.VLine)
        self.topColLine.setLineWidth(1)
        self.topColLine.setStyleSheet("QFrame { color: gray; height: 2px; }")
        
        self.top_bar.addLayout(self.top_column_1)
        self.top_bar.addWidget(self.topColLine)
        self.top_bar.addLayout(self.top_column_2)
        
        # Bottom Bar
        self.bottom_bar = QVBoxLayout()
        self.bottom_bar.setAlignment(Qt.AlignCenter)
        self.bottom_bar.setSpacing(5)
        self.bottom_bar.setContentsMargins(0,0,0,0)
        # 1st Row
        self.bottom_row_1 = QHBoxLayout()
        self.bottom_row_1.setSpacing(5)
        self.bottom_row_1.setContentsMargins(0,0,0,0)
        
        self.enter_skill_button = QPushButton("Enter Skill (C)")
        self.enter_skill_button.clicked.connect(self.emit_skill_creation)
        self.enter_skill_button.setEnabled(False)
        self.enter_skill_button.setCursor(Qt.PointingHandCursor)
        self.enter_skill_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        
        self.enter_action_button = QPushButton("Enter Action (F)")
        self.enter_action_button.setCursor(Qt.PointingHandCursor)
        self.enter_action_button.clicked.connect(self.emit_action_creation)
        self.enter_action_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.enter_action_button.setEnabled(False)
        
        self.fill_quick_action_button = QPushButton("Fill Quick Action (Shift+Q)")
        self.fill_quick_action_button.setCursor(Qt.PointingHandCursor)
        self.fill_quick_action_button.clicked.connect(self.emit_fill_action_creation)
        self.fill_quick_action_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.fill_quick_action_button.setEnabled(False)
        
        self.bottom_row_1.addWidget(self.fill_quick_action_button)
        self.bottom_row_1.addWidget(self.enter_action_button)
        self.bottom_row_1.addWidget(self.enter_skill_button)
        # 2nd Row
        self.bottom_row_2 = QHBoxLayout()
        self.bottom_row_2.setSpacing(5)
        self.bottom_row_2.setContentsMargins(0,0,0,0)
        
        self.zoom_button = QPushButton("Zoom Selection (Shift+Z)")
        self.zoom_button.setCursor(Qt.PointingHandCursor)
        self.zoom_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.zoom_button.setEnabled(False)
        
        
        self.bottom_row_2.addWidget(self.zoom_button)
        
        self.bottom_bar.addLayout(self.bottom_row_1)
        self.bottom_bar.addLayout(self.bottom_row_2)
        #================
        
        self.middleLine = QFrame()
        self.middleLine.setFrameShape(QFrame.HLine)
        self.middleLine.setLineWidth(1)
        self.middleLine.setFixedWidth(450)
        self.middleLine.setStyleSheet("QFrame { color: gray; height: 2px; }")
        
        self.setFixedHeight(300)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10,10,10,10)
        self.setLayout(self.layout)
        self.layout.addLayout(self.top_bar)
        self.layout.addWidget(self.middleLine, alignment=Qt.AlignCenter)
        self.layout.addLayout(self.bottom_bar)
        
        self.has_start = False
        self.has_end = False
    
    def enable_enter_button(self):
        if self.has_start and self.has_end:
            self.enter_action_button.setEnabled(True)
            self.enter_skill_button.setEnabled(True)
            self.zoom_button.setEnabled(True)
            self.fill_quick_action_button.setEnabled(True)
        else:
            self.enter_action_button.setEnabled(False)
            self.enter_skill_button.setEnabled(False)
            self.zoom_button.setEnabled(False)
            self.fill_quick_action_button.setEnabled(False)
    
    def set_skill_name(self, name):
        self.enter_skill_name.setText(name)
    
    def set_start(self):
        self.SetStart.emit()
        self.has_start = True
        self.enable_enter_button()
    
    def set_end(self):
        self.SetEnd.emit()
        self.has_end = True
        self.enable_enter_button()
        
    def emit_quick_action(self):
        self.EnterQuickAction.emit(self.enter_skill_name.text())
        
    def emit_fill_action_creation(self):
        if self.fill_quick_action_button.isEnabled():
            self.EnterFillAction.emit(self.enter_skill_name.text())
    
    def emit_action_creation(self):
        if self.enter_action_button.isEnabled():
            self.EnterAction.emit(self.enter_skill_name.text())
    
    def emit_skill_creation(self):
        if self.enter_skill_button.isEnabled():
            self.EnterSkill.emit(self.enter_skill_name.text())
            
    def skill_entered(self):
        self.has_start = False
        self.has_end = False
        self.enable_enter_button()