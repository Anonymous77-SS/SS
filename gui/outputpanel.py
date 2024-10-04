from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout, QScrollArea
from gui.colortheme import CustomColorTheme


class ExceptionLog(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(0,0,0,0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.setAttribute(Qt.WA_StyledBackground) 
        #self.setAutoFillBackground(True)
        self.setStyleSheet("""
            QWidget{
                padding: 5px;
            }""")
        
        self.loglayout = QVBoxLayout()
        self.setLayout(self.loglayout)
        self.loglayout.setSpacing(1)
        self.loglayout.setAlignment(Qt.AlignTop)
        
class LastError(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #self.setAttribute(Qt.WA_StyledBackground) 
        #self.setAutoFillBackground(True)
        self.setStyleSheet("""
            QWidget{
                padding: 5px;
            }""")
        
        self.loglayout = QVBoxLayout()
        self.setLayout(self.loglayout)
        self.loglayout.setSpacing(2)
        self.loglayout.setAlignment(Qt.AlignTop)

class OutputPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setFixedWidth(600)

        self.lasterrortitle = QLabel("Last Message")
        self.lasterrortitle.setStyleSheet(f"{CustomColorTheme.BOLD_FONT_1} background-color: {CustomColorTheme.ACCENT}; color: white; padding: 4px;")
        
        self.errormsg = QLabel("")
        self.errormsg.setStyleSheet(f"{CustomColorTheme.MONO_FONT_2} color: red;")
        self.errormsg.setWordWrap(True) 
        
        self.lasterror = LastError()        
        self.lasterror.loglayout.addWidget(self.errormsg)
        
        self.errorscroll_area = QScrollArea()
        self.errorscroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.errorscroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.errorscroll_area.setWidgetResizable(True)
        self.errorscroll_area.setWidget(self.lasterror)
        self.errorscroll_area.setStyleSheet(CustomColorTheme.get_scroll_log_style("QScrollArea"))
        
        self.validationtitle = QLabel("Validation Log")
        self.validationtitle.setStyleSheet(f"{CustomColorTheme.BOLD_FONT_1} background-color: {CustomColorTheme.ACCENT}; color: white; padding: 4px;")
        
        self.exceptionarea = ExceptionLog()
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setWidget(self.exceptionarea)
        self.scroll_area.setStyleSheet(CustomColorTheme.get_scroll_log_style("QScrollArea"))
        
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.addWidget(self.lasterrortitle)
        self.layout.addWidget(self.errorscroll_area, stretch=1)
        self.layout.addWidget(self.validationtitle)
        self.layout.addWidget(self.scroll_area , stretch=2)
        
    def update_error(self,exception):
        self.errormsg.setText(str(exception))
        self.update()
        
    def clear_error(self):
        self.errormsg.setText("")
        self.update()
    
    def update_log(self, exception_list):
        while self.exceptionarea.loglayout.count():
            item = self.exceptionarea.loglayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            del item
        
        for exception in exception_list:
            stylesheet = CustomColorTheme.MONO_FONT_2
            if exception.type == "Error":
                label = QLabel(f"-ERROR: {exception}")
                stylesheet +="color: red;"
            elif exception.type == "Warning":
                label = QLabel(f"-WARNING: {exception}")
                stylesheet +="color: yellow;"
            else:
                label = QLabel(f"- {exception}")
                stylesheet +="color: white;"
                
            label.setStyleSheet(stylesheet)
            self.exceptionarea.loglayout.addWidget(label)
        self.exceptionarea.update()
        self.update()