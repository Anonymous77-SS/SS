from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy,QComboBox, QPushButton, QVBoxLayout, QFileDialog, QStyle, QHBoxLayout, QStatusBar
from PyQt5.QtGui import QImage, QPixmap, QColor
import cv2

from gui.colortheme import CustomColorTheme

class VideoWorker(QObject):
    PreviewImageFrameUpdate = pyqtSignal(QImage) #,QImage,QImage) # frame
    CurrImageFrameUpdate = pyqtSignal(QImage) # frame
    ImageInfoUpdate = pyqtSignal(float, int, int, int, int, int) # fps, curr_frame, min_frame, max_frame, height, width
    
    def __init__(self):
        super().__init__()
        self.fpsSync = QTimer()
        self.prev_fps = 0
        self.fps = 60
        self.fpsSync.setInterval((int)(1000 // self.fps))
        
        self.playing = False
        self.cap = None
        self.cap_fps = 0
        self.cap_frames = 0
        self.cap_height = 0
        self.cap_width = 0
        self.curr_frame = 0
        
        self.curr_img = None
        self.next_img = None
        
        self.min_frame = 0
        self.max_frame = self.cap_frames
                
        #self.load_video("minigrid.mp4")
        
        self.fpsSync.timeout.connect(self.run)
        self.fpsSync.start()
    
    def generate_empty_frame(self):
        f = QImage(self.cap_height, self.cap_width, QImage.Format_RGB32)
        f.fill(QColor(0, 0, 0))
        return f
    
    def run(self):
        prev_frame = self.curr_frame
        prev_fps = self.cap_fps
        prev_min_frame = self.min_frame
        prev_max_frame = self.max_frame
        if self.playing:                
            self.emit_frame(self.curr_frame+1)
        elif prev_frame != self.curr_frame or prev_fps != self.cap_fps or prev_min_frame != self.min_frame or prev_max_frame != self.max_frame:
            self.ImageInfoUpdate.emit(self.cap_fps, int(self.curr_frame), int(self.min_frame), int(self.max_frame), self.cap_height, self.cap_width)
        
    def emit_frame(self, frame=None):
        if self.prev_fps != self.fps:
            self.fpsSync.setInterval((int)(1000 // self.fps))
            self.prev_fps = self.fps
             
        regenAll = False
        if frame is None:
            regenAll = True
            frame = self.curr_frame+1
        elif frame != self.curr_frame+1:
            regenAll = True
            
        if frame > self.max_frame:
            # No need to update if we are at the end of the video
            return False
        elif frame == self.curr_frame:
            # No need to update if we are at the same frame
            return False
                
        # GENERATE NEXT IMG
        prev_next_img = self.next_img
        if frame+1 <= self.max_frame:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame + 1)
            next_ret, next_video_frame = self.cap.read()
            h, w, ch = next_video_frame.shape
            next_video_frame = cv2.cvtColor(next_video_frame, cv2.COLOR_BGR2RGB)
            bytes_per_line = ch * w
            self.next_img = QImage(next_video_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        else:
            self.next_img = self.generate_empty_frame()
        
        # EMIT CURR
        self.curr_frame = frame
        self.ImageInfoUpdate.emit(self.cap_fps, int(self.curr_frame), int(self.min_frame), int(self.max_frame), self.cap_height, self.cap_width)
        
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.curr_frame)
        if regenAll:
            ret, video_frame = self.cap.read()
            if ret:
                rgb_image = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.curr_img = convert_to_qt_format
        else:
            self.curr_img = prev_next_img
        print(f"FPS: {self.fps}, Curr Frame: {self.curr_frame}, Min Frame: {self.min_frame},\
            Max Frame: {self.max_frame} Height: {self.cap_height}, Width: {self.cap_width}")
    
            
    def get_frame(self):
        return self.curr_img
    
    def get_next_frame(self):
        return self.next_img
    
    def load_video(self, video_path):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(video_path)
        self.curr_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.cap_frames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)-1 # Last frame is empty
        cap_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        
        if (cap_height < cap_width):
            #Landscape
            cap_height = min(cap_height, 1080)
            cap_width = int(cap_height * (cap_width / cap_height))
        else:
            #Portrait
            cap_width = min(cap_width, 1080)
            cap_height = int(cap_width * (cap_height / cap_width))
            
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, cap_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cap_height)
        
        self.cap_height = cap_height
        self.cap_width = cap_width
        
        self.curr_img = None
        self.next_img = None
        
        self.fps = self.cap_fps
        self.min_frame = float(self.curr_frame) # frame 0 is NOT nothing
        self.max_frame = self.cap_frames
        
        self.video_path = video_path
        self.emit_frame()
        self.set_frame(self.min_frame)
    
    def play(self):
        self.playing = True
        
    def pause(self):
        self.playing = False
          
    def stop(self):
        self.ThreadActive = False
        self.cap.release()
        self.quit()
    
    def set_frame(self, frame, external=False):
        # Prevent async issues
        if external and self.playing:
            return
        
        # We want to prevent the frame from going out of bounds
        if frame > self.max_frame:
            frame = self.max_frame
        elif frame < self.min_frame:
            frame = self.min_frame
            
        self.emit_frame(frame)
        self.ImageInfoUpdate.emit(self.cap_fps, int(self.curr_frame), int(self.min_frame), int(self.max_frame), self.cap_height, self.cap_width)
        
    def change_video_bounds(self,start_frame, end_frame, external=False):
        if external and self.playing:
            return
        self.min_frame = start_frame
        self.max_frame = end_frame
        self.set_frame(self.curr_frame)
    
    def forward(self, frames):
        new_frame_val = min(self.cap_frames, self.curr_frame + frames)
        self.set_frame(new_frame_val)
    
    def backward(self, frames):
        new_frame_val = max(0, self.curr_frame - frames)
        self.set_frame(new_frame_val)
        
class VideoContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.setAttribute(Qt.WA_OpaquePaintEvent)
        
        # Create Media player
        self.center_feed = QLabel(self,alignment=Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.mini_label = QLabel("Next Frame",self)
        self.mini_label.setStyleSheet(f"{CustomColorTheme.BOLD_FONT_3} background: transparent; color: white;")
        
        self.center_label = QLabel("Current Frame",self)
        self.center_label.setStyleSheet(f"{CustomColorTheme.BOLD_FONT_2} background: transparent; color: white;")
        self.position_next_frame_label()
        
        self.mini_feed = QLabel(self,alignment=Qt.AlignCenter)
        self.mini_feed.setMinimumSize(100, 100)
        
        self.update_dimensions(self.width(), self.height())
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_image)
        self.timer.start(1000 // 30)
        
        # Video Worker that Handles Stream
        self.video_worker = VideoWorker()
        #self.video_worker_thread = QThread()
        #self.video_worker.moveToThread(self.video_worker_thread)
        #self.video_worker_thread.start()
                
    def update_dimensions(self, width, height):
        self.center_feed.resize(width, height)
        scale = 4
        self.mini_feed.setFixedSize(self.center_feed.width()//scale, self.center_feed.height()//scale)
    
    def position_next_frame_label(self):
        self.center_label.move(5, self.height() - self.center_label.height())
        
    def resizeEvent(self, event):
        self.timer.stop()
        self.update_dimensions(event.size().width(),event.size().height())
        
        
        if self.center_feed.pixmap() is not None:
            scaled_pixmap = self.center_feed.pixmap().scaled(self.center_feed.size(), aspectRatioMode=Qt.KeepAspectRatio, transformMode= Qt.SmoothTransformation)
            self.center_feed.setPixmap(scaled_pixmap)
        self.position_next_frame_label()
        super().resizeEvent(event)
        
        # top right
        self.mini_feed.move(self.width()-self.mini_feed.width(),0)
        self.mini_label.move(self.mini_feed.pos())
        self.timer.start()
        
    def update_image(self):
        frame = self.video_worker.get_frame()
        next_frame = self.video_worker.get_next_frame()
        if next_frame is not None:
            self.mini_feed.setPixmap(QPixmap.fromImage(next_frame.scaled(self.mini_feed.width(), self.mini_feed.height(), Qt.KeepAspectRatio, transformMode= Qt.SmoothTransformation)))
        if frame is not None:
            self.center_feed.setPixmap(QPixmap.fromImage(frame.scaled(self.center_feed.width(),self.center_feed.height(), Qt.KeepAspectRatio, transformMode= Qt.SmoothTransformation)))
        self.mini_label.raise_()
        self.center_label.raise_()
        
class VideoControls(QWidget):
    TogglePlay = pyqtSignal(bool)
    ForwardVideo = pyqtSignal(int)
    BackwardVideo = pyqtSignal(int)
    ChangeFps = pyqtSignal(float)
    ResetZoom = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.control_height = 40
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("VideoControls")
        self.setStyleSheet(f"#VideoControls {{ background-color: {CustomColorTheme.ACCENT_1}; }} ")
        
        self.setFixedHeight(self.control_height)
        
        self.button_width = 32
        self.button_height = 32
        self.btn_size = QSize(self.button_width, self.button_height)
        
        self.play_button = QPushButton()
        self.play_button.setCursor(Qt.PointingHandCursor)
        self.play_button.setFixedSize(self.btn_size)
        self.play_button.setIconSize(self.btn_size)
        self.play_button_state = False
        self.pause_video()
        self.play_button.clicked.connect(self.toggle_video_play)
        self.play_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton",CustomColorTheme.PAUSE))
        
        self.forward_button = QPushButton()
        self.forward_button.setCursor(Qt.PointingHandCursor)
        self.forward_button.setFixedSize(self.btn_size)
        self.forward_button.setIconSize(self.btn_size)
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekForward))
        self.forward_button.clicked.connect(self.forward_video)
        self.forward_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        
        self.backward_button = QPushButton()
        self.backward_button.setCursor(Qt.PointingHandCursor)
        self.backward_button.setFixedSize(self.btn_size)
        self.backward_button.setIconSize(self.btn_size)
        self.backward_button.setIcon(self.style().standardIcon(QStyle.SP_MediaSeekBackward))
        self.backward_button.clicked.connect(self.backward_video)
        self.backward_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        
        self.fps_select = QComboBox()
        self.fps_select.setStyleSheet(CustomColorTheme.FONT_2)
        self.fps_select.setCursor(Qt.PointingHandCursor)
        self.fps_select.addItems([".05x", ".1x", ".25x", ".5x", "1x", "1.5x", "2.0x"])
        self.fps_select.setCurrentIndex(4)
        self.fps_select.currentTextChanged.connect(self.change_fps)
        
        self.reset_zoom_button = QPushButton("Reset Zoom (R)")
        self.reset_zoom_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        self.reset_zoom_button.setCursor(Qt.PointingHandCursor)
        self.reset_zoom_button.setFixedHeight(self.button_height)
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.reset_zoom_button)
        self.layout.addWidget(self.backward_button)
        self.layout.addWidget(self.play_button)
        self.layout.addWidget(self.forward_button)
        self.layout.addWidget(self.fps_select)
    
    def reset_zoom(self):
        self.ResetZoom.emit()
    
    def change_fps(self,text):
        self.ChangeFps.emit(float(text.replace("x", "")))
     
    def toggle_video_play(self):
        if self.play_button_state:
            self.pause_video()
        else:
            self.play_video()
    
    def play_video(self):
        self.play_button_state = True
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton",CustomColorTheme.PLAY))
        self.TogglePlay.emit(self.play_button_state)
      
    def pause_video(self):
        self.play_button_state = False
        self.play_button.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.play_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton",CustomColorTheme.PAUSE))
        self.TogglePlay.emit(self.play_button_state)
    
    def forward_video(self):
        self.ForwardVideo.emit(1)
    
    def backward_video(self):
        self.BackwardVideo.emit(1)

class OpenVideo(QWidget):
    def __init__(self):
        super().__init__()
        self.control_height = 30
        
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("OpenVideo")
        self.setStyleSheet(f"#OpenVideo {{ background-color: {CustomColorTheme.ACCENT_1}; }} ")

        self.setFixedHeight(self.control_height)
        
        self.open_button = QPushButton("Open Video")
        self.open_button.setCursor(Qt.PointingHandCursor)
        self.open_button.setStyleSheet(CustomColorTheme.get_button_2_style("QPushButton"))
        
        self.file_name = QStatusBar()
        self.file_name.setStyleSheet(f"{CustomColorTheme.FONT_3}")
        self.file_name.showMessage("No video selected.")
        
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.open_button)
        self.layout.addWidget(self.file_name)

class VideoPlayer(QWidget):
    ResetZoom = pyqtSignal(float, float)
    def __init__(self):
        super().__init__()       
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.video_widget = VideoContainer()
        
        self.video_controls = VideoControls()
        self.video_controls.TogglePlay.connect(self.toggle_play)
        self.video_controls.ForwardVideo.connect(self.forward_video)
        self.video_controls.BackwardVideo.connect(self.backward_video)
        self.video_controls.ChangeFps.connect(self.change_fps)
        self.video_controls.ResetZoom.connect(self.reset_zoom)
    
        self.open_video = OpenVideo()
        self.aspect_ratio = 9/16
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)
        self.layout.addWidget(self.open_video)
        self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.video_controls)
    
    def update_dimensions(self, width, height):
        video_width = width
        video_height = int(video_width * self.aspect_ratio)
        
        # If the height is out of bounds, we need to readjust
        if video_height > height:
            video_height = height
            video_width = int(video_height / self.aspect_ratio)
        return video_width, video_height
       
    
    def toggle_play(self,state):
        if state:
            self.video_widget.video_worker.play()
        else:
            self.video_widget.video_worker.pause()
            
    def reset_zoom(self):
        self.ResetZoom.emit(0, self.video_widget.video_worker.cap_frames)
        
    def zoom_selection(self, start_frame, end_frame):
        self.video_widget.video_worker.change_video_bounds(start_frame, end_frame, True)
    
    def change_fps(self, fps):
        default_fps = self.video_widget.video_worker.cap_fps
        self.video_widget.video_worker.fps = fps * default_fps
    
    def forward_video(self, frames):
        self.video_widget.video_worker.forward(frames)
    
    def backward_video(self, frames):
        self.video_widget.video_worker.backward(frames)
        
    def load_video_from_file(self):
        # Pause video if playing
        self.video_controls.pause_video()
        # Open File Dialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if file_path:
            # Load Video
            self.load_video(file_path)
            return True
        return False
    
    def load_video(self, video_path):
        self.video_widget.video_worker.load_video(video_path)
        self.open_video.file_name.showMessage(video_path)