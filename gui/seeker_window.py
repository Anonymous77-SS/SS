from PyQt5.QtCore import Qt, QSize, pyqtSignal, QPoint, QEvent
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy
from PyQt5.QtGui import QResizeEvent
from sortedcontainers import SortedDict

from gui import util
from gui.colortheme import CustomColorTheme

class FrameWidget(QWidget):
    HoverFrame = pyqtSignal(bool)
    def __init__(self, color, type):
        super(FrameWidget, self).__init__()
        self.type = type
        self.color = color
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.set_default_style()
        
        self.installEventFilter(self)
        
    def set_default_style(self):
        if self.type == "action":
            color = util.generate_alternating_gradient(self.color,util.lighten_hex_color(self.color,.2))
        else:
            color = self.color
        self.setStyleSheet(f"background-color: {color};")
        
    def hover_on(self):
        if self.type == "action":
            color = util.generate_alternating_gradient(util.lighten_hex_color(self.color,.2),util.lighten_hex_color(self.color,.4))
        else:
            color = util.lighten_hex_color(self.color,.2)
        self.setStyleSheet(f"border: 1px solid white; background-color: {color};")
    
    def hover_off(self):
        self.set_default_style()
    
    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Enter:
                self.HoverFrame.emit(True)
            elif event.type() == QEvent.Leave:
                self.HoverFrame.emit(False)
        return super().eventFilter(obj, event)
    
class SeekerBar(QWidget):
    def __init__(self,height,parent=None,type=None):
        super().__init__(parent)
        
        self.handle_size = 10
        self.bar_height = height
        self.bar_width = 4
        
        if type == "start":
            self.color = CustomColorTheme.PLAY
        elif type == "end":
            self.color = CustomColorTheme.PAUSE
        else:
            self.color = "white"
        
        self.bar = QWidget(self)
        self.bar.setFixedSize(self.bar_width, self.bar_height)
        self.bar.setStyleSheet(f"background-color: {self.color}; border: 1px solid black;")
        self.bar.move(self.handle_size//2-self.bar_width//2,self.handle_size//2)
        
        self.tophandle = QWidget(self)
        self.tophandle.setFixedSize(self.handle_size, self.handle_size)
        self.tophandle.setStyleSheet(f"background-color: {self.color}; border: 1px solid black;")
        
        self.bottomhandle = QWidget(self)
        self.bottomhandle.setFixedSize(self.handle_size, self.handle_size)
        self.bottomhandle.setStyleSheet(f"background-color: {self.color}; border: 1px solid black;")
        self.bottomhandle.move(0, self.bar_height)
    
    def get_x_offset(self):
        return self.handle_size//2
    
    def move_corrected(self,pos):
        # Put in position of MIDDLE of handle
        pos.setX(pos.x() - self.get_x_offset())
        self.move(pos)
    
    def get_corrected_pos(self):
        pos = self.pos()
        pos.setX(pos.x() + self.get_x_offset())
        return pos    
        
        
class SeekerWindow(QWidget):
    SeekFrame = pyqtSignal(float, bool)
    def __init__(self):
        super().__init__()
        
        self.setAttribute(Qt.WA_StyledBackground) 
        self.setObjectName("SeekerWindow")
        
        self.setContentsMargins(0,0,0,0)
        
        
        self.bar_height = 50
        self.bar_margin_top = 10
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.bar_width = self.width()
        self.setFixedHeight(self.bar_height+self.bar_margin_top*2)
        
        self.bar = QWidget(self)
        self.bar.setFixedHeight(self.bar_height)
        self.bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.bar.setStyleSheet(f"background-color: {CustomColorTheme.TIMELINE};")
        self.bar.move(0,self.bar_margin_top)
        
        self.seekerbar = SeekerBar(self.bar_height+self.bar_margin_top,self)
        self.seekerbar.setCursor(Qt.SplitHCursor)
        self.seekerbar.move(-self.seekerbar.get_x_offset(),0)
        self.seekerbar_frame = 0
        self.dragging = False
        self.min_frame = 0
        self.max_frame = 0
        
        self.recalculate_max_ticks()
        self.ticks = []
        self.frame_seek_positions = []
        self.frame_seek_frames = []
        
        self.startbar = SeekerBar(self.bar_height+self.bar_margin_top,self,"start")
        self.startbar_frame = 0
        self.startbar.hide()
        
        self.endbar = SeekerBar(self.bar_height+self.bar_margin_top,self,"end")
        self.endbar_frame = 0
        self.endbar.hide()
        
        self.widgetInfo = dict()
        self.items = SortedDict()
        
    def recalculate_max_ticks(self):
        self.max_ticks = self.bar_width
        
    def resizeEvent(self, event):
        width = event.size().width()
        self.bar_width = width
        self.recalculate_max_ticks()
        self.bar.setFixedWidth(self.bar_width)
        self.generate_ticks(self.min_frame,self.max_frame)
        for key,frame_item in self.items.items():
            start_frame, end_frame = key[0], -key[1]
            self.mod_skill(frame_item, start_frame, end_frame)
        self.update()
        super().resizeEvent(event)
        
    def update_skills(self, tree):
        # Different items- remove from sidebar
        selected_skills = [(w[0].value,w[1]) for w in tree.traverse(levels=True)]
            
        skill_uuids = set([(skill.frame_start,-skill.frame_end, skill.uuid) for (skill,level) in selected_skills])
        difference_remove = set(self.items.keys()).difference(set(skill_uuids))
        
        for skill in difference_remove:
            removed_item = self.items.pop(skill)
            removed_item.setParent(None)
            removed_item.deleteLater()
            
        # Different items- add to sidebar
        for skill,level in selected_skills:
            new_key = (skill.frame_start,-skill.frame_end, -level, skill.uuid) 
            if new_key not in self.items:
                frame_item = FrameWidget(skill.get_color(),skill.type)
                frame_item.setParent(self.bar)
                tree.connect_framewidget(skill.uuid, frame_item)
                start_frame, end_frame = skill.frame_start, skill.frame_end
                self.mod_skill(frame_item, start_frame, end_frame)
                self.items[new_key] = frame_item
                self.items[new_key].show()
            else:
                self.items[new_key].show()
                
        for frame_item in self.items.values():
            frame_item.raise_()
        self.update()
    
    def mod_skill(self,frame_widget, start_frame, end_frame):
        self.widgetInfo[frame_widget] = (start_frame, end_frame)
        frame_widget.setParent(self.bar)
        start_position = self.frame_to_pos(start_frame)
        end_position = self.frame_to_pos(end_frame)
        width = end_position - start_position
        if width == 0:
            width = 3 # We need to have a width
        frame_widget.setFixedSize(int(width),self.bar_height)
        frame_widget.move(int(start_position),0)
        #frame_widget.raise_()
        frame_widget.show()
        #print("Added overlay from", start_frame, "to", end_frame)
    
    def frame_to_pos(self, frame):
        if len(self.frame_seek_frames)==0:
            return 0
        
        closest_frame_index = 0
        for i, seek_frame in enumerate(self.frame_seek_frames):
            if frame < seek_frame:
                break
            closest_frame_index = i
        
        past_frame = self.frame_seek_frames[closest_frame_index]
        next_frame = self.frame_seek_frames[closest_frame_index] if closest_frame_index == len(self.frame_seek_frames)-1 else self.frame_seek_frames[closest_frame_index+1]
        
        #print("Current frame", frame, "Past frame", past_frame, "Next frame", next_frame)
        if next_frame == past_frame:
            percent_between_frames = 1
        else:
            percent_between_frames = (frame-past_frame)/(next_frame-past_frame)
        
        past_pos = self.frame_seek_positions[closest_frame_index]
        next_pos = self.frame_seek_positions[closest_frame_index] if closest_frame_index == len(self.frame_seek_positions)-1 else self.frame_seek_positions[closest_frame_index+1]
        
        true_pos = past_pos + percent_between_frames*(next_pos-past_pos)
        
        return int(true_pos)
    
    def pos_to_frame(self, pos):
        if len(self.frame_seek_frames)==0:
            return 0
        
        closest_pos_index = 0
        for i, seek_pos in enumerate(self.frame_seek_positions):
            if pos < seek_pos:
                break
            closest_pos_index = i
            
        # past_pos = self.frame_seek_positions[closest_pos_index]
        past_frame = self.frame_seek_frames[closest_pos_index]
        return past_frame
    
    def clear_bars(self):
        self.startbar_frame = 0
        self.startbar.hide()
        self.endbar_frame = 0
        self.endbar.hide()
    
    def set_start(self):
        self.startbar_frame = self.seekerbar_frame
        self.startbar.move(self.seekerbar.pos())
        self.startbar.show()
        print("Setting start at frame", self.startbar_frame)
    
    def set_end(self):
        self.endbar_frame = self.seekerbar_frame
        self.endbar.move(self.seekerbar.pos())
        self.endbar.show()
        print("Setting end at frame", self.endbar_frame)
    
    def send_seekerbar_frame(self):
        print("Sending seekerbar frame", self.seekerbar_frame)
        return self.seekerbar_frame
    
    def send_skill_frames(self):
        print("Sending skill frames", self.startbar_frame, self.endbar_frame)
        return self.startbar_frame, self.endbar_frame
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            event.accept()
        
    def update(self):
        self.bar.lower()
        for tick in self.ticks:
            tick.raise_()
        new_seekbar_pos = self.frame_to_pos(self.seekerbar_frame)
        self.seekerbar.move_corrected(QPoint(new_seekbar_pos,0))
        new_startbar_pos = self.frame_to_pos(self.startbar_frame)
        self.startbar.move_corrected(QPoint(new_startbar_pos,0))
        new_endbar_pos = self.frame_to_pos(self.endbar_frame)
        self.endbar.move_corrected(QPoint(new_endbar_pos,0))
        self.startbar.raise_()
        self.endbar.raise_()
        self.seekerbar.raise_()
        super().update()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            x_pos = event.pos().x()
            #
            if x_pos < 0:
                x_pos = 0
            elif x_pos > self.bar.width():
                x_pos = self.bar.width()
            self.seekerbar.move_corrected(QPoint(x_pos,0))
            self.SeekFrame.emit(self.pos_to_frame(x_pos), True)
            self.update()
            event.accept()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
    
    def generate_equally_spaced_integers(self,start, end, count,include_end=False):
        if count == 1:
            return [start]
        step = (end - start) / (count - 1)
        numbers = [round(start + (step) * i) for i in range(count)]
        
        # Ensure the last number is exactly 'end'
        if include_end:
            numbers[-1] = end
        return numbers

    def calc_tick_frames(self, min_frame, max_frame):
        num_frames = int(max_frame - min_frame+1)
        num_ticks = min(num_frames,self.max_ticks)
        
        self.frame_seek_positions = self.generate_equally_spaced_integers(int(0+1), int(self.bar_width-1), num_ticks)
        self.frame_seek_frames = self.generate_equally_spaced_integers(int(min_frame), int(max_frame), num_ticks, include_end= True)
        
        if len(self.frame_seek_positions) != len(self.frame_seek_frames):
            raise Exception(
                "Frame positions and frames not equal. Positions",
                len(self.frame_seek_positions),
                "Frames",
                len(self.frame_seek_frames),
                "Expected:",
                num_ticks,
                "Min Frame:",
                min_frame,
                "Max Frame:",
                max_frame)
    
    def generate_ticks(self, min_frame, max_frame):
        self.calc_tick_frames(min_frame, max_frame)
        
        for tick in self.ticks:
            tick.deleteLater()
        self.ticks = []
        # num_ticks = min(len(self.frame_seek_positions),self.max_ticks)
        tick_width = 3
        for i in range(0,len(self.frame_seek_positions),tick_width):
            label = QLabel(self) #str(self.frame_seek_positions[i])
            label.setAttribute(Qt.WA_StyledBackground) 
            label.setStyleSheet(f"background-color: {CustomColorTheme.TICK_MARK};")
            label.setFixedHeight(self.bar_margin_top)
            label.setFixedWidth(tick_width)
            label.move(int(self.frame_seek_positions[i]-tick_width//2),0)
            label.show()
            self.ticks.append(label)
        
        print("Length ticks", len(self.ticks), "Length positions", len(self.frame_seek_positions), "Length frames", len(self.frame_seek_frames))
    
    def receive_playback(self,curr_frame,min_frame,max_frame):
        change_selection = self.max_frame != max_frame or self.min_frame != min_frame
        self.max_frame = max_frame
        self.min_frame = min_frame
        self.seekerbar_frame = curr_frame
                    
        position = int(self.frame_to_pos(curr_frame))
        #print("Percent",int(((curr_frame-min_frame)/(max_frame-min_frame))))
        self.seekerbar.move_corrected(QPoint(position,0))
        
        if change_selection:
            print("Changing selection to", min_frame, max_frame)
            self.resizeEvent(QResizeEvent(QSize(self.bar_width,self.height()),QSize(self.bar_width,self.height())))
        else:
            self.update()