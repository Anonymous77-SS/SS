import hashlib

class ActionUnit():
    type = "action"
    full_valid_colors = [
        "#B52D4F",
        "#E83E25",
        "#E8D025",
        "#28719C",
        "#4299BC",
        "#429483",
        "#25C88D",
        "#88B740",
        "#358F2B",
        "#314450",
        "#3D5131",
        "#53545F",
        "#514982",
        "#8441B3",
        "#B73A98",
        "#BD6D9A",
        "#A35163",
        "#A16855",
        "#845D36",
        "#A68852",
        
    ]

    name_to_color_map = {}
    
    def __init__(self, uuid, name, frame_start, frame_end):
        self.uuid = uuid
        self.name = name
        self.frame_start = frame_start
        self.frame_end = frame_end
        
        # Check if new color needs to be added
        if name not in ActionUnit.name_to_color_map:
            ActionUnit.name_to_color_map[name] = ActionUnit.gen_hex_color(name)
        
        print("Adding skill", name, "with color", ActionUnit.name_to_color_map[name])
    
    def gen_hex_color(name):
        hash_name = hashlib.sha256(name.encode('ascii'))
        color_index = int(str(hash_name.hexdigest()), 16) % len(ActionUnit.full_valid_colors)
        
        color = ActionUnit.full_valid_colors[color_index]
        return color
    
    def get_color(self):
        return ActionUnit.name_to_color_map[self.name]
    
    def update(self, name, frame_start, frame_end):
        self.name = name
        self.frame_start = frame_start
        self.frame_end = frame_end
    
    def __eq__(self, other):
        if isinstance(other, ActionUnit):
            return self.frame_start == other.frame_start and self.frame_end == other.frame_end
        raise ValueError(f"Cannot compare {type(self)} with type {type(other)}")
    
    def __lt__(self, other):
        if isinstance(other, ActionUnit):
            return (self.frame_start < other.frame_start) or (self.frame_start == other.frame_start and self.frame_end > other.frame_end)
        raise ValueError(f"Cannot compare {type(self)} with type {type(other)}")
    
    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)
    
    def __gt__(self, other):
        if isinstance(other, ActionUnit):
            return self.frame_start > other.frame_start or (self.frame_start == other.frame_start and self.frame_end < other.frame_end)
        raise ValueError(f"Cannot compare {type(self)} with type {type(other)}")
    
    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)
    
    def __hash__(self):
        return hash((self.uuid, self.name, self.type, self.frame_start, self.frame_end))
    
    def __repr__(self):
        return f"[{self.type}]{self.name}({self.uuid}): [{self.frame_start},{self.frame_end}]"


class SkillUnit(ActionUnit):
    type = "skill"
    def __init__(self, uuid, name, frame_start, frame_end):
        super().__init__(uuid, name, frame_start, frame_end)