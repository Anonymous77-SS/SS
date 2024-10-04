# This allows for us to run files internally in the folder if need be
try:
    from data_structure.skillunit import ActionUnit, SkillUnit
except ImportError:
    from data_structure.skillunit import ActionUnit, SkillUnit


class InconsistentType(Exception):
    type = "Error"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"'{self.name}' is used as both {SkillUnit.__name__} and {ActionUnit.__name__}."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, InconsistentType):
            return self.name == o.name
        return False
    
    
class NonPythonicName(Exception):
    type = "Warning"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"'{self.name}' is a non-pythonic name."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, NonPythonicName):
            return self.name == o.name
        return False 

class VideoFileNotFound(Exception):
    type = "Error"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Video file '{self.name}' could not be found."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, VideoFileNotFound):
            return self.name == o.name
        return False
    
class FileEncodingFailure(Exception):
    type = "Error"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"File '{self.name}' could not be encoded."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, FileEncodingFailure):
            return self.name == o.name
        return False
    
class FrameNotFound(Exception):
    type = "Error"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Frame '{self.name}' not found."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, FrameNotFound):
            return self.name == o.name
        return False
    
class InvalidFile(Exception):
    type = "Error"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"'{self.name}' is an invalid file."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, InvalidFile):
            return self.name == o.name
        return False