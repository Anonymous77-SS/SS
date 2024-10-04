class OverlappingSkills(Exception):
    type = "Error"
    def __init__(self, name, range_start, range_end, child_name, child_range_start, child_range_end):
        self.name = name
        self.range_start = range_start
        self.range_end = range_end
        self.child_name = child_name
        self.child_range_start = child_range_start
        self.child_range_end = child_range_end
    
    def __str__(self) -> str:
        return f"Cannot insert '{self.name}' with range [{self.range_start}, {self.range_end}] due to overlap with '{self.child_name}' with range [{self.child_range_start}, {self.child_range_end}]."
    
    def __hash__(self) -> int:
        return hash(self.name, self.range_start, self.range_end, self.child_name, self.child_range_start, self.child_range_end)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, OverlappingSkills):
            return self.name == o.name and self.range_start == o.range_start and self.range_end == o.range_end and self.child_name == o.child_name and self.child_range_start == o.child_range_start and self.child_range_end == o.child_range_end
        return False

class ActionHasChildren(Exception):
    type = "Error"
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return f"Action '{self.name}' cannot have children."

    def __hash__(self) -> int:
        return hash(self.name)
    
    def __eq__(self, o: object) -> bool:
        if isinstance(o, ActionHasChildren):
            return self.name == o.name
        return False 