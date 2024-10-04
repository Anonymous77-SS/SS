from collections import deque
from pathlib import Path
import sys
import uuid
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication, QFrame, QWidget, QMainWindow, QVBoxLayout, QFileDialog, QHBoxLayout
from PyQt5.QtGui import QIcon, QKeySequence
from gui.colortheme import CustomColorTheme
from gui.exceptions import InconsistentType, InvalidFile, NonPythonicName, VideoFileNotFound
from data_structure.exceptions import OverlappingSkills, ActionHasChildren
from gui.hotkey_bar import HotkeyBar
from gui.serializer import ProgressDialog, Serializer
from gui.video_player import VideoPlayer
from gui.seeker_window import SeekerWindow
from gui.skill import NaryRangeTreeSkillSegaWrapper, SkillCreator
from data_structure.skillunit import ActionUnit, SkillUnit
from gui.sidebar import Sidebar
from data_structure.naryrangetree import NaryRangeTree
from gui.outputpanel import OutputPanel


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.update_window_title(None)
        self.setWindowIcon(QIcon('icon.png'))
        
        self.setObjectName("MainWindow")
        self.setStyleSheet(f"QMainWindow {{background-color: {CustomColorTheme.BACKGROUND};}}")
        
        self.setFocusPolicy(Qt.StrongFocus)
        self.window = SkillSega()
        self.window.UpdateTitle.connect(self.update_window_title)
        self.setCentralWidget(self.window)
        
        menubar = self.menuBar()
        hotkey_menu = menubar.addMenu("&Hotkeys")
        
        toggle_play_action = hotkey_menu.addAction("Toggle Play/Pause")
        toggle_play_action.triggered.connect(self.window.video_player.video_controls.toggle_video_play)
        toggle_play_action.setShortcut(QKeySequence("Space"))
        
        backward_action = hotkey_menu.addAction("Backward 1 Frame")
        backward_action.triggered.connect(self.window.video_player.video_controls.backward_video)
        backward_action.setShortcut(QKeySequence("A"))
        
        forward_action = hotkey_menu.addAction("Forward 1 Frame")
        forward_action.triggered.connect(self.window.video_player.video_controls.forward_video)
        forward_action.setShortcut(QKeySequence("D"))
        
        set_start_action = hotkey_menu.addAction("Set Start Frame")
        set_start_action.triggered.connect(self.window.skill_creator.set_start)
        set_start_action.setShortcut(QKeySequence("W"))
        
        set_end_action = hotkey_menu.addAction("Set End Frame")
        set_end_action.triggered.connect(self.window.skill_creator.set_end)
        set_end_action.setShortcut(QKeySequence("S"))
        
        quick_action = hotkey_menu.addAction("Quick Action")
        quick_action.triggered.connect(self.window.skill_creator.emit_quick_action)
        quick_action.setShortcut(QKeySequence("Q"))
        
        fill_quick_action = hotkey_menu.addAction("Fill Quick Action")
        fill_quick_action.triggered.connect(self.window.skill_creator.emit_fill_action_creation)
        fill_quick_action.setShortcut(QKeySequence("Shift+Q"))
        
        create_action_action = hotkey_menu.addAction("Create Action")
        create_action_action.triggered.connect(self.window.skill_creator.emit_action_creation)
        create_action_action.setShortcut(QKeySequence("F"))
        
        create_skill_action = hotkey_menu.addAction("Create Skill")
        create_skill_action.triggered.connect(self.window.skill_creator.emit_skill_creation)
        create_skill_action.setShortcut(QKeySequence("C"))
        
        quick_zoom_action = hotkey_menu.addAction("Quick Zoom Selection")
        quick_zoom_action.triggered.connect(self.window.quick_zoom_frame_selection)
        quick_zoom_action.setShortcut(QKeySequence("Z"))
        
        zoom_selection_action = hotkey_menu.addAction("Zoom Selection")
        zoom_selection_action.triggered.connect(self.window.zoom_frame_selection)
        zoom_selection_action.setShortcut(QKeySequence("Shift+Z"))
        
        reset_zoom_selection_action = hotkey_menu.addAction("Zoom Selection")
        reset_zoom_selection_action.triggered.connect(self.window.video_player.reset_zoom)
        reset_zoom_selection_action.setShortcut(QKeySequence("R"))
        
        open_action = hotkey_menu.addAction("Open Sega File")
        open_action.triggered.connect(self.window.import_skills)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        
        undo_action = hotkey_menu.addAction("Undo")
        undo_action.triggered.connect(self.window.undo)
        undo_action.setShortcut(QKeySequence("Ctrl+Z"))

        redo_action = hotkey_menu.addAction("Redo")
        redo_action.triggered.connect(self.window.redo)
        redo_action.setShortcut(QKeySequence("Ctrl+Y"))

        save_action = hotkey_menu.addAction("Save Sega File")
        save_action.triggered.connect(self.window.export_skills_save)
        save_action.setShortcut(QKeySequence("Ctrl+S"))
        
        save_as_action = hotkey_menu.addAction("Save Sega File As")
        save_as_action.triggered.connect(self.window.export_skills_save_as)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        
        expand_window_action = hotkey_menu.addAction("Expand Window")
        expand_window_action.triggered.connect(self.show_maximized)
        expand_window_action.setShortcut(QKeySequence("Ctrl+="))
        
        collapse_window_action = hotkey_menu.addAction("Collapse Window")
        collapse_window_action.triggered.connect(self.show_collapsed)
        collapse_window_action.setShortcut(QKeySequence("Ctrl+-"))
        
        fullscreen_window_action = hotkey_menu.addAction("Toggle Fullscreen Window")
        fullscreen_window_action.triggered.connect(self.toggle_fullscreen)
        fullscreen_window_action.setShortcut(QKeySequence("F11"))
        
        hotkey_menu.addAction(open_action)
        hotkey_menu.addSeparator()
        hotkey_menu.addAction(undo_action)
        hotkey_menu.addAction(redo_action)
        hotkey_menu.addSeparator()
        hotkey_menu.addAction(save_action)
        hotkey_menu.addAction(save_as_action)
        hotkey_menu.addSeparator()
        hotkey_menu.addAction(toggle_play_action)
        hotkey_menu.addAction(backward_action)
        hotkey_menu.addAction(forward_action)
        
        hotkey_menu.addAction(set_start_action)
        hotkey_menu.addAction(set_end_action)
        
        hotkey_menu.addAction(create_skill_action)
                
        hotkey_menu.addAction(quick_action)
        hotkey_menu.addAction(fill_quick_action)
        
        
        hotkey_menu.addAction(quick_zoom_action)
        hotkey_menu.addAction(zoom_selection_action)
        hotkey_menu.addAction(reset_zoom_selection_action)
        
        hotkey_menu.addSeparator()
        hotkey_menu.addAction(expand_window_action)
        hotkey_menu.addAction(collapse_window_action)
        hotkey_menu.addAction(fullscreen_window_action)
        
        self.resize(1600,900)
        
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def update_window_title(self,file_path):
        self.setWindowTitle(f"SkillSega - {'No Save File' if file_path is None else file_path}")
        
    def show_collapsed(self):
        # pause to prevent crash
        self.window.video_player.video_controls.pause_video()
        self.resize(1600,900)
    
    def show_maximized(self):
        # pause to prevent crash
        self.window.video_player.video_controls.pause_video()
        self.showMaximized()
            
class SkillSega(QWidget):
    UpdateTitle = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        
        self.current_file_path = None
                
        self.video_player = VideoPlayer()
        self.video_player.ResetZoom.connect(self.zoom_selection)
        self.video_player.video_widget.video_worker.ImageInfoUpdate.connect(self.transmit_frame_info)
        self.video_player.open_video.open_button.clicked.connect(self.load_video)
        
        self.seeker_window = SeekerWindow()
        self.seeker_window.SeekFrame.connect(self.video_player.video_widget.video_worker.set_frame)
        
        self.skill_creator = SkillCreator()
        self.skill_creator.quick_zoom.clicked.connect(self.quick_zoom_frame_selection)
        self.skill_creator.zoom_button.clicked.connect(self.zoom_frame_selection)
        self.skill_creator.SetStart.connect(self.seeker_window.set_start)
        self.skill_creator.SetEnd.connect(self.seeker_window.set_end)
        self.skill_creator.EnterSkill.connect(self.trigger_create_skill)
        self.skill_creator.EnterAction.connect(self.trigger_create_action)
        self.skill_creator.EnterQuickAction.connect(self.trigger_quick_action)
        self.skill_creator.EnterFillAction.connect(self.trigger_quick_fill_action)
        
        self.hotkey_bar = HotkeyBar()
        self.hotkey_bar.skill_sidebar.SetName.connect(self.skill_creator.set_skill_name)
        
        self.sidebar = Sidebar()
        self.sidebar.import_bar.import_button.clicked.connect(self.import_skills)
        self.sidebar.import_bar.export_button.clicked.connect(self.export_skills_save_as)
        
        self.vLine_1 = QFrame()
        self.vLine_1.setFrameShape(QFrame.VLine)
        self.vLine_1.setLineWidth(2)
        self.vLine_1.setStyleSheet("QFrame { color: grey; border: 2px solid grey;}")
        
        self.vLine_2 = QFrame()
        self.vLine_2.setFrameShape(QFrame.VLine)
        self.vLine_2.setLineWidth(2)
        self.vLine_2.setStyleSheet("QFrame { color: grey; border: 2px solid grey;}")
        
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        self.mainlayout = QVBoxLayout()
        self.mainlayout.setContentsMargins(0, 0, 0, 0)
        self.mainlayout.setSpacing(0)
        
        self.videolayout = QHBoxLayout()
        self.videolayout.setContentsMargins(0, 0, 0, 0)
        self.videolayout.setSpacing(0)
        self.videolayout.addWidget(self.video_player)
        self.videolayout.addWidget(self.vLine_1)
        self.videolayout.addWidget(self.hotkey_bar)
        
        self.outputpanel = OutputPanel()
        
        self.bottomlayout = QHBoxLayout()
        self.bottomlayout.addWidget(self.outputpanel)
        self.bottomlayout.addWidget(self.skill_creator)
        
        self.mainlayout.addLayout(self.videolayout)
        self.mainlayout.addWidget(self.seeker_window)
        self.mainlayout.addLayout(self.bottomlayout)

        self.layout.addLayout(self.mainlayout)
        self.layout.addWidget(self.vLine_2)
        self.layout.addWidget(self.sidebar)
        
        self.skills = NaryRangeTreeSkillSegaWrapper(NaryRangeTree())
        
        # Stacks for undo/redo
        num_actions_saved = 50
        self.undo_stack = deque(maxlen=num_actions_saved)
        self.redo_stack = deque(maxlen=num_actions_saved)        
    
    def log_action(self, action, dict):
        # Add action to undo stack and clear redo stack
        self.undo_stack.append((action, dict))
        self.redo_stack = deque()
        
    def undo(self):
        if len(self.undo_stack) == 0:
            return
        # pop top element from undo stack
        last_action, dict = self.undo_stack.pop()
        
        # perform the action
        reverse_action, new_dict = self.reverse_action(last_action, dict)
        self.parse_action(reverse_action, new_dict)
        
        # push element onto redo stack
        self.redo_stack.append((last_action, dict))
    
    def redo(self):
        if len(self.redo_stack) == 0:
            return
        # pop the top element of redo stack
        last_action, dict = self.redo_stack.pop()
        
        # perform the action
        self.parse_action(last_action, dict)
        
        # push element onto undo stack
        self.undo_stack.append((last_action, dict))
    
    def reverse_action(self, action, dict):
        if action == "create_skill":
            return "delete_skill", dict
        elif action == "delete_skill":
            return "create_skill", dict
        if action == "create_action":
            return "delete_action", dict
        elif action == "delete_action":
            return "create_action", dict
        elif action == "create_quick_fill_action":
            return "delete_quick_fill_action", dict
        elif action == "delete_quick_fill_action":
            return "create_quick_fill_action", dict
        else:
            raise Exception("Invalid reverse action", action)
    
    def parse_action(self, action, dict):
        if action == "create_skill":
            skill_name = dict["skill_name"]
            skill_uuid = dict["skill_uuid"]
            start_frame = dict["start_frame"]
            end_frame = dict["end_frame"]
            self.create_skill(skill_name, skill_uuid, start_frame, end_frame)
        elif action == "delete_skill":
            skill_uuid = dict["skill_uuid"]
            self.delete_skill(skill_uuid)
        elif action == "create_action":
            skill_name = dict["skill_name"]
            skill_uuid = dict["skill_uuid"]
            start_frame = dict["start_frame"]
            end_frame = dict["end_frame"]
            self.create_action(skill_name, skill_uuid, start_frame, end_frame)
        elif action == "delete_action":
            skill_uuid = dict["skill_uuid"]
            self.delete_skill(skill_uuid)
        elif action == "create_quick_fill_action":
            skill_name = dict["skill_name"]
            skill_uuids = dict["skill_uuids"]
            start_frame = dict["start_frame"]
            end_frame = dict["end_frame"]
            frames = range(start_frame, end_frame+1)
            for skill_uuid, frame in zip(skill_uuids,frames):
                self.create_action(skill_name, skill_uuid, frame, frame, noRefresh=True)
            self.transmit_skills()
        elif action == "delete_quick_fill_action":
            skill_uuids = dict["skill_uuids"]
            for skill_uuid in skill_uuids:
                self.delete_skill(skill_uuid, noRefresh=True)
            self.transmit_skills()
        else:
            raise Exception("Invalid action", action)
    
    def load_video(self):
        loaded_video = self.video_player.load_video_from_file()
        if loaded_video:
            self.delete_all_skills()
            self.undo_stack.clear()
            self.redo_stack.clear()
    
    def update_window_title(self,file_path):
        self.current_file_path = file_path
        self.UpdateTitle.emit(file_path)
        
    def import_skills(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Skills", "", "SEGA Files (*.sega)")
        if file_path:
            if not file_path.lower().endswith('.sega'):
                self.outputpanel.update_error(InvalidFile(file_path))
                return
        if file_path:
            serializer = Serializer()
            try:
                video_path, dict_data = serializer.deserialize(file_path)
            except VideoFileNotFound as e:
                self.outputpanel.update_error(e)
            else:
                self.outputpanel.clear_error()
                self.skills.clear()
                for key,value in dict_data.items():
                    if "type" not in value:
                        new_item = SkillUnit(uuid.UUID(key), value["name"], value["start"], value["end"])
                    elif value["type"] == "action":
                        new_item = ActionUnit(uuid.UUID(key), value["name"], value["start"], value["end"])
                    else:
                        new_item = SkillUnit(uuid.UUID(key), value["name"], value["start"], value["end"])
                    self.skills.insert(new_item,value["start"], value["end"], self.trigger_delete_skill, self.zoom_selection)
                    
                self.video_player.load_video(video_path)
                self.update_window_title(file_path)
                self.transmit_skills()
    
    def print_rec(self,node,num_tab= 0):
        for child in node.children:
            print("\t"*num_tab, child.value.name, child.value.frame_start, child.value.frame_end)
            self.print_rec(child,num_tab+1)
    
    def export_skills_save(self):
        if self.current_file_path is None:
            self.export_skills_save_as()
        else:
            filename = self.current_file_path
            self.save_skills(filename)
    
    def export_skills_save_as(self):
        video_path = Path(self.video_player.video_widget.video_worker.video_path)
        suggested_file_name = video_path.stem
        filename, _ = QFileDialog.getSaveFileName(
                None,
                "Save File",
                suggested_file_name,
                "SEGA Files (*.sega)"
            )
        if filename:
            if not filename.lower().endswith('.sega'):
                filename += '.sega'
        
        print(f"File will be saved as: {filename}")
        self.save_skills(filename)

    def save_skills(self, filename):
        if filename:
            video_path = self.video_player.video_widget.video_worker.video_path
            
            self.progress_dialog = ProgressDialog(self)
            self.progress_dialog.save_file(video_path, self.skills, filename)
            self.progress_dialog.exec_()
            
            if self.progress_dialog.exception:
                self.outputpanel.update_error(self.progress_dialog.exception)
            else:
                self.outputpanel.clear_error()
                self.update_window_title(filename)
                
            self.progress_dialog.deleteLater()
        
    def transmit_skills(self):
        unique_uuids = set()
        error_uuids = set()
        print("Traversal:")
        for s in self.skills.traverse():
            print(s)
            if s.value.uuid in unique_uuids:
                error_uuids.add(s.value.uuid)
            if s.value.uuid not in unique_uuids:
                unique_uuids.add(s.value.uuid)
        print("End Traversal")
        if error_uuids:
            print("=====================================")
            print("ERROR:", error_uuids)
            print("=====================================")
        self.sidebar.skill_sidebar.update_skills(self.skills)
        self.seeker_window.update_skills(self.skills)
        self.generate_debug()
    
    def quick_zoom_frame_selection(self):
        curr_frame = self.seeker_window.send_seekerbar_frame()
        
        # Find skill that contains the current frame
        # If there is no skill, this will return a None value with -inf, inf
        selected_skill = self.skills.query_value_with_tightest_range_containing(curr_frame)
        if selected_skill.value:
            start_frame = selected_skill.range_start
            end_frame = selected_skill.range_end
            self.zoom_selection(start_frame, end_frame)
        else:
            self.video_player.reset_zoom()
            
    def zoom_frame_selection(self):
        if self.skill_creator.zoom_button.isEnabled():
            start_frame = self.seeker_window.startbar_frame
            end_frame = self.seeker_window.endbar_frame
            self.zoom_selection(start_frame, end_frame)
    
    def zoom_selection(self, start_frame, end_frame):
        self.video_player.zoom_selection(start_frame, end_frame)
        self.transmit_skills()
    
    def generate_debug(self):
        print("Generating debug")
        action_names = set()
        skill_names = set()
        
        errors = set()
        
        for skill_node in self.skills.traverse():
            if type(skill_node.value) is ActionUnit:
                if skill_node.value.name in skill_names:
                    errors.add(InconsistentType(skill_node.value.name))
                else:
                    action_names.add(skill_node.value.name)
            else:
                if skill_node.value.name in action_names:
                    errors.add(InconsistentType(skill_node.value.name))
                else:
                    skill_names.add(skill_node.value.name)
            if not skill_node.value.name.isidentifier():
                errors.add(NonPythonicName(skill_node.value.name))
                    
        print("Errors:", errors)
        self.outputpanel.update_log(errors)
    
    def verify_frames(self, start_frame, end_frame):
        if start_frame > end_frame:
            print("Invalid frame range")
            return False
        return True
    
    def trigger_quick_action(self, action_name):
        frame = self.seeker_window.send_seekerbar_frame()
        end_frame = frame + 1        
        action_uuid = uuid.uuid4()

        self.create_action(action_name, action_uuid, frame, end_frame, noRefresh=False)
        self.log_action("create_action", {"skill_name": action_name, "skill_uuid": action_uuid, "start_frame": frame, "end_frame": end_frame})

    def trigger_quick_fill_action(self, action_name):
        start_frame, end_frame = self.seeker_window.send_skill_frames()
        valid = self.verify_frames(start_frame, end_frame)
        if valid:
            self.seeker_window.clear_bars()
            self.skill_creator.skill_entered()
            action_uuids = []
            chosen_frames = range(int(start_frame), int(end_frame))
            
            # If we are going to generate no frames, just don't do anything
            if chosen_frames == []:
                return
            
            for curr_start_frame in chosen_frames:
                curr_end_frame = curr_start_frame + 1
                action_uuid = uuid.uuid4()
                action_uuids.append(action_uuid)
                self.create_action(action_name, action_uuid, curr_start_frame, curr_end_frame, noRefresh=True)
                
            self.transmit_skills()
            self.log_action("create_quick_fill_action", {"skill_name": action_name, "skill_uuids": action_uuids, "start_frame": start_frame, "end_frame": end_frame})

    
    def trigger_create_skill(self, skill_name):
        start_frame, end_frame = self.seeker_window.send_skill_frames()
        valid = self.verify_frames(start_frame, end_frame)
        if valid:
            skill_uuid = uuid.uuid4()
            self.seeker_window.clear_bars()
            self.skill_creator.skill_entered()
            self.create_skill(skill_name, skill_uuid, start_frame, end_frame)
            self.log_action("create_skill", {"skill_name": skill_name, "skill_uuid": skill_uuid, "start_frame": start_frame, "end_frame": end_frame})
            
    def trigger_create_action(self, action_name):
        start_frame, end_frame = self.seeker_window.send_skill_frames()
        valid = self.verify_frames(start_frame, end_frame)
        if valid:
            action_uuid = uuid.uuid4()
            self.seeker_window.clear_bars()
            self.skill_creator.skill_entered()
            self.create_action(action_name, action_uuid, start_frame, end_frame)
            self.log_action("create_action", {"skill_name": action_name, "skill_uuid": action_uuid, "start_frame": start_frame, "end_frame": end_frame})
    
    def create_action(self, action_name, action_uuid, start_frame, end_frame, noRefresh=False):
        print("Creating action", action_name, "from", start_frame, "to", end_frame)
        new_action = ActionUnit(action_uuid, action_name, start_frame, end_frame)
        try:
            self.skills.insert(new_action,start_frame,end_frame, self.trigger_delete_action, self.zoom_selection)
            if not noRefresh:
                self.transmit_skills()
        except (OverlappingSkills, ActionHasChildren) as e:
            self.outputpanel.update_error(e)
            
        else:
            self.outputpanel.clear_error()
            
    def create_skill(self, skill_name, skill_uuid, start_frame, end_frame, noRefresh=False):
        print("Creating skill", skill_name, "from", start_frame, "to", end_frame)
        new_skill = SkillUnit(skill_uuid, skill_name, start_frame, end_frame)
        try:
            self.skills.insert(new_skill,start_frame,end_frame, self.trigger_delete_skill, self.zoom_selection)
            if not noRefresh:
                self.transmit_skills()
        except (OverlappingSkills, ActionHasChildren) as e:
            self.outputpanel.update_error(e)
        else:
            self.outputpanel.clear_error()
    
    def delete_all_skills(self):
        for skill_node in self.skills.traverse():
            uuid = skill_node.value.uuid
            emission = self.skills.skill_emissions[uuid]
            emission.deleteLater()
        self.skills.clear()
        self.transmit_skills()
    
    def trigger_delete_action(self, uuid):
        skill_name, start_frame, end_frame = self.delete_skill(uuid)
        self.log_action("delete_action", {"skill_name": skill_name, "skill_uuid": uuid, "start_frame": start_frame, "end_frame": end_frame})
    
    
    def trigger_delete_skill(self, uuid):
        skill_name, start_frame, end_frame = self.delete_skill(uuid)
        self.log_action("delete_skill", {"skill_name": skill_name, "skill_uuid": uuid, "start_frame": start_frame, "end_frame": end_frame})
    
    def delete_skill(self, uuid, noRefresh = False):
        # for node in self.skills.traverse():
        #     print(node)
        # Remove skill with uuid: assume first. Should retrieve removed object for proper cleanup
        lambda_func = lambda x: x.uuid == uuid
        skill, emission = self.skills.pop(lambda_func)
        skill = skill.value
        #print("Found Deleting skill", skill.uuid, skill.name, skill.frame_start, skill.frame_end)
        emission.deleteLater()
        if not noRefresh:
            self.transmit_skills()
        return skill.name, skill.frame_start, skill.frame_end
        
    def transmit_frame_info(self,fps,curr_frame,min_frame,max_frame,width,height):
        self.seeker_window.receive_playback(curr_frame,min_frame,max_frame)


if __name__ == "__main__":    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    player = Window()
    player.show()
    
    sys.exit(app.exec_())