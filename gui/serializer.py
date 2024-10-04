import io
import os
from pathlib import Path
import pickle
import zipfile
import cv2
import json
from gui.exceptions import FileEncodingFailure, FrameNotFound, VideoFileNotFound
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QProgressBar, QDialog, QVBoxLayout
from dataclasses import dataclass

@dataclass
class StackItem:
    call_fun: callable
    call_arg: list 
    sub_fun: callable
    sub_arg: list
    counter: int 
    ret_val: int
    
class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Processing...")
        self.setModal(True)  # Make the dialog modal to grey out everything behind it
        
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        
        layout = QVBoxLayout()
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)
        
        self.exception = None
        
        self.serializer = Serializer()
        self.serializer_thread = QThread()
        self.serializer.moveToThread(self.serializer_thread)
        self.serializer_thread.started.connect(self.serializer.run)
        self.serializer.Progress.connect(self.progress_bar.setValue)
        self.serializer.Finished.connect(self.task_finished)
        self.serializer.Exception.connect(self.exception_caught)
        
    def exception_caught(self, e):
        self.serializer_thread.quit()
        self.exception = e
        self.reject()
    
    def save_file(self, video_path, skills, filename):
        self.progress_bar.setValue(0)
        self.serializer.init_serializer(video_path, skills, filename)
        self.serializer_thread.start()
        
    def task_finished(self):
        self.serializer_thread.quit()
        self.exception = None
        self.accept()
        
class Serializer(QObject):
    Progress = pyqtSignal(int)
    Exception = pyqtSignal(Exception)
    Finished = pyqtSignal()
    _videopath = "_videopath"
    _temp_file = "_temp"
    def __init__(self):
        super().__init__()
    
    def init_serializer(self, video_path, skills, save_path):
        self.video_path = video_path
        self.skills = skills
        self.save_path = Path(save_path)
        
    def finishSuccess(self):
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
            print(f"Deleted old file: {self.save_path}")
        os.rename(self._temp_file, self.save_path)
        self.Finished.emit()
        
    def finishException(self, e):
        if os.path.exists(self._temp_file):
            os.remove(self._temp_file)
            print(f"Deleted temporary file: {self._temp_file}")
        self.Exception.emit(e)
        
    def run(self):
        # num_skills = 50
        # for i in range(1,num_skills+1):
        #     time.sleep(0.2)
        #     self.progress = int(i/num_skills*100)
        #     print(i,num_skills,int(i/num_skills*100))
        #     self.Progress.emit(int(i/num_skills*100))
        # self.Finished.emit()
                
        if os.path.exists(self._temp_file):
            os.remove(self._temp_file)
            print(f"Deleted temporary file: {self._temp_file}")
        with zipfile.ZipFile(self._temp_file, 'w') as zipf:
                print(f"Created temp file: {self._temp_file}")
                pass  # Create an empty .sega file
        
        
        # Load video
        cap = cv2.VideoCapture(self.video_path)
        #
        skill_dict = {}
        skills = [skill.value for skill in self.skills.traverse()]
        num_progress = len(skills)+1
        saved_frames = set()
        for i,skill in enumerate(skills, 1):
            skill_type = skill.type
            skill_name = skill.name
            skill_uuid = skill.uuid
            start_frame = int(skill.frame_start)
            end_frame = int(skill.frame_end)
            #Find all desired frames
            for f in range(start_frame, end_frame + 1): 
                print("Frame",f)
                if f not in saved_frames:
                    saved_frames.add(f)
                    cap.set(cv2.CAP_PROP_POS_FRAMES, f)
                    ret, video_frame = cap.read()
                    if ret is False:
                        return self.finishException(FrameNotFound(f))
                        
                    success, buffer = cv2.imencode('.png', video_frame)
                    if not success:
                        return self.finishException(FileEncodingFailure(f"{video_frame}.png"))
                    byte_stream = io.BytesIO(buffer)
                    
                    # Add the image to the .sega archive
                    with zipfile.ZipFile(self._temp_file, 'a') as zipf:
                        zipf.writestr(f"{f}.png",byte_stream.getvalue())
                    
            skill_dict[str(skill_uuid)] = {"name": skill_name, "type": skill_type, "start": start_frame, "end": end_frame}
            self.Progress.emit(int(i/num_progress*100))
             
        skill_dict[self._videopath] = str(self.video_path)  
        json_str = json.dumps(skill_dict,indent=None) 
        byte_stream = io.BytesIO(json_str.encode('utf-8'))
        with zipfile.ZipFile(self._temp_file, 'a') as zipf:
            zipf.writestr("data.json", byte_stream.getvalue())
            pickled_skill_tree = pickle.dumps(self.skills.dewrap())
            zipf.writestr("skilltree.pkl", pickled_skill_tree)

        self.Progress.emit(int(num_progress/num_progress*100))
        
        return self.finishSuccess()

    def deserialize(self, path):
        path = Path(path)
        
        with zipfile.ZipFile(path, 'r') as zipf:
            with zipf.open("data.json") as file:
                # Read the JSON data
                json_data = file.read().decode('utf-8')
                # Deserialize the JSON data
                data = json.loads(json_data)
        
        video_path = data.pop(self._videopath)
        if not os.path.exists(video_path):
            raise VideoFileNotFound(video_path)
        
        return video_path, data