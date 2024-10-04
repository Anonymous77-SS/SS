from PyQt5.QtCore import Qt, QSize, pyqtSignal, QEvent
from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QAction, QSizePolicy, QPushButton, QVBoxLayout, QStyle, QHBoxLayout, QScrollArea
from PyQt5.QtGui import QCursor, QFont
import numpy as np
from sortedcontainers import SortedDict
from gui import util
from gui.colortheme import CustomColorTheme

class SidebarItem(QWidget):
    HoverSidebar = pyqtSignal(bool)
    VisibleChanged = pyqtSignal()
    def __init__(self, name, type, frame_start, frame_end, color):
        super().__init__()
        self.setObjectName("outerWidget")
        
        self.type = type
        self.name = name
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.color = color
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.item_height = 30
        self.setFixedHeight(self.item_height)
       
        self.internal_height = self.item_height - 2
        
        self.name_label = QLabel()
        self.name_label.setFixedHeight(self.internal_height)
        if self.type == "action":
            font = QFont('Arial', 12, QFont.Light)
            font.setItalic(True)
            self.name_label.setFont(font)   
        else:
            self.name_label.setFont(QFont('Arial', 12, QFont.Bold))   
        self.name_label.setStyleSheet("padding: 2px;")
        
        self.frame_info_label = QLabel()
        self.frame_info_label.setFixedHeight(self.internal_height)
        self.frame_info_label.setFont(QFont('Arial', 12, QFont.Bold))
        self.frame_info_label.setStyleSheet("padding: 2px;")
        
        self.update_data(name, frame_start, frame_end)     
        
        self.icn_size = QSize(4+(self.internal_height//2), self.internal_height)
        self.btn_size = QSize(self.internal_height//2, self.internal_height//2)
        
        self.zoom_button = QPushButton()
        self.zoom_button.setIconSize(self.btn_size)
        self.zoom_button.setFixedSize(self.icn_size)
        self.zoom_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        self.zoom_button.setFocusPolicy(Qt.NoFocus)
        self.zoom_button.setFlat(True)
        self.zoom_button.setCursor(Qt.PointingHandCursor)
        self.zoom_button.raise_()
        
        self.delete_button = QPushButton() 
        self.delete_button.setIconSize(self.btn_size)
        self.delete_button.setFixedSize(self.icn_size)
        self.delete_button.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.delete_button.setFocusPolicy(Qt.NoFocus)
        self.delete_button.setFlat(True)
        self.delete_button.setCursor(Qt.PointingHandCursor)
        self.delete_button.raise_()
        
        self.nestbutton = QPushButton()
        self.nestbutton_size = QSize(15, self.internal_height)
        self.nestbutton.setFixedSize(self.nestbutton_size)
        self.nestbutton.setCheckable(True)
        self.nestbutton.setChecked(False)
        self.nestbutton.toggled.connect(self.toggle_nest_button)
        self.nestbutton.setCursor(Qt.PointingHandCursor)
        self.nestbutton.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.toggle_nest_button()
        self.nestbutton.hide()
        
        self.nestlayout = QHBoxLayout()
        self.nestlayout.setSpacing(5)
        
        self.layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(2,0,2,0)
        self.layout.addLayout(self.nestlayout)
        self.layout.addWidget(self.nestbutton)
        self.layout.addWidget(self.name_label)
        self.layout.addStretch(1)
        self.layout.addWidget(self.frame_info_label)
        self.layout.addWidget(self.zoom_button)
        self.layout.addWidget(self.delete_button)
        
        self.name_label.setStyleSheet("margin-left: 5px; border: 0px solid black;")
        self.zoom_button.setStyleSheet("background-color: red; border: 1px solid black;")
        self.delete_button.setStyleSheet("background-color: blue; border: 1px solid black;")
        self.set_default_style()     
        self.installEventFilter(self)
    
    def toggle_nest_button(self):
        if self.nestbutton.isChecked():
            self.nestbutton.setText(">")
        else:
            self.nestbutton.setText("⌄")
    
    def contextMenuEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        # Create a context menu
        context_menu = QMenu(self)
        
        # Change cursor to pointer when inside the context menu
        context_menu.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Create actions for the menu
        zoom_action = QAction("Zoom", self)
        delete_action = QAction("Delete", self)

        # Connect actions to their respective methods
        zoom_action.triggered.connect(self.zoom_button.click)
        delete_action.triggered.connect(self.delete_button.click)

        # Add actions to the context menu
        context_menu.addAction(zoom_action)
        context_menu.addAction(delete_action)
        
        context_menu.setStyleSheet("""
            QMenu{
                background-color: #303031;
                color:"white";
            }
            QMenu::item:selected{
                background-color: #49494a;
            }
            """)

        # Display the context menu at the cursor position
        context_menu.exec_(event.globalPos())
        self.unsetCursor()
        
    def generate_nest_indicator(self):
        nest_indicator = QWidget()
        nest_indicator.setFixedWidth(3)
        nest_indicator.setFixedHeight(self.height())
        nest_indicator.setStyleSheet("background-color: white; padding-left: 3px; padding-right: 3px;")

        nest_indicator.raise_()
        self.nestlayout.insertWidget(0, nest_indicator)
        
    def update_nests(self, nest_count, has_children):
        # Update nest indicators
        while self.nestlayout.count() > 0:
            item = self.nestlayout.takeAt(0)  # Take the item from the layout
            widget = item.widget()  # Get the widget from the item
            if widget is not None:
                widget.deleteLater()  # Mark the widget for deletion
            del item  # Delete the item
        
        if nest_count > 1:
            self.nestlayout.setContentsMargins(5,0,0,0)
            for i in range(nest_count-1):
                self.generate_nest_indicator()
        else:
            self.nestlayout.setContentsMargins(0,0,0,0)
                
        # Add collapse button if there are children
        if has_children:
            self.nestbutton.show()
        else:
            self.nestbutton.hide()
            
        self.update()
    
    def hideEvent(self, event):
        super().hideEvent(event)
        self.VisibleChanged.emit()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.VisibleChanged.emit()
    
    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Enter:
                self.HoverSidebar.emit(True)
            elif event.type() == QEvent.Leave:
                self.HoverSidebar.emit(False)
        return super().eventFilter(obj, event)
    
    
    def set_default_style(self):
        if self.type == "action":
            color = util.generate_alternating_gradient(self.color,util.lighten_hex_color(self.color,.2))
        else:
            color = self.color
        self.setStyleSheet(f"#outerWidget {{ background-color: {color}; }}")
        
    def hover_on(self):
        if self.type == "action":
            color = util.generate_alternating_gradient(util.lighten_hex_color(self.color,.2),util.lighten_hex_color(self.color,.4))
        else:
            color = util.lighten_hex_color(self.color,.2)
        self.setStyleSheet(f"#outerWidget {{ background-color: {color}; border: 1px solid white; }} ")
        
    def hover_off(self):
        self.set_default_style()
    
    def update_data(self, name, frame_start, frame_end):
        self.name = name
        self.frame_start = frame_start
        self.frame_end = frame_end
        
        self.name_label.setText(f"{name}")
        self.frame_info_label.setText(f"[{frame_start},{frame_end}]")
        self.update()


class SkillBar(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.items = SortedDict()
    
    def update_skills(self, tree):
        selected_skills = [w for w in tree.traverse(levels=True)]
        skills = []
        levels = []
        has_children = []
        for skill, level in selected_skills:
            skills.append(skill.value)
            levels.append(level)
            has_children.append(len(skill.children) > 0)
            
        # Different items- remove from sidebar
        skill_uuids = set([(skill.frame_start,-skill.frame_end,skill.uuid) for skill in skills])
        difference_remove = set(self.items.keys()).difference(set(skill_uuids))
        
        for skill in difference_remove:
            removed_item = self.items.pop(skill)
            self.layout.removeWidget(removed_item)
            removed_item.deleteLater()
            
        for skill,level,has_children in zip(skills,levels,has_children):
            # Different items- add to sidebar
            new_key = (skill.frame_start,-skill.frame_end,level,skill.uuid) 
            if new_key not in self.items:
                sidebar_item = SidebarItem(skill.name, skill.type, skill.frame_start, skill.frame_end, skill.get_color())
                sidebar_item.update_nests(level, has_children)
                sidebar_item.VisibleChanged.connect(self.adjustSize)
                tree.connect_sidebar(skill.uuid,sidebar_item)
                self.items[new_key] = sidebar_item
                index_loc = self.items.index(new_key)
                self.layout.insertWidget(index_loc, sidebar_item)
                self.items[new_key].show()
            else:
                self.items[new_key].update_nests(level, has_children)
                self.items[new_key].show()
            # Same items- update sidebar
            # Nothing needs to be done 
        self.adjustSize()
        self.update()
    
    def adjustSize(self):
        height = 0
        for i in range(self.layout.count()):
            item = self.layout.itemAt(i)
            if item.widget().isVisible():
                height += item.widget().height()
        self.setFixedHeight(height)
        
class ImportBar(QWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {CustomColorTheme.ACCENT_1};")
        
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(50)
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.setSpacing(40)
        
        self.import_button = QPushButton("Import")
        self.import_button.setCursor(Qt.PointingHandCursor)
        self.import_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        
        self.export_button = QPushButton("Export")
        self.export_button.setCursor(Qt.PointingHandCursor)
        self.export_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        
        self.layout.addWidget(self.import_button)
        self.layout.addWidget(self.export_button)
        
class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setContentsMargins(0,0,0,0)
        width = 350
        self.setFixedWidth(width)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        self.skill_sidebar = SkillBar()
        self.skill_sidebar.setFixedWidth(width-15)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("scroll_area")
        
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidget(self.skill_sidebar)
        self.scroll_area.setAttribute(Qt.WA_StyledBackground, True) 
        self.scroll_area.setStyleSheet(CustomColorTheme.get_scroll_accent_style("#scroll_area"))
        
        self.import_bar = ImportBar()
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.import_bar)