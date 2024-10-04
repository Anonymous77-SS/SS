import unittest

# This allows for us to have unittests in the same file as the class definition
try:
    from data_structure.exceptions import ActionHasChildren, OverlappingSkills
    from data_structure.skillunit import ActionUnit, SkillUnit
except ImportError:
    from exceptions import ActionHasChildren, OverlappingSkills
    from skillunit import ActionUnit, SkillUnit

class NaryRangeTreeNode:
    def __init__(self, value, range_start, range_end):
        self.value = value
        self.range_start = range_start
        self.range_end = range_end
        self.children = []

    def __repr__(self):
        return f"Node({self.value}, Range: [{self.range_start}, {self.range_end}]): {[child.value for child in self.children]}"
    
    def __eq__(self, other):
        if not isinstance(other, NaryRangeTreeNode):
            return False
        return self.value == other.value and self.range_start == other.range_start and self.range_end == other.range_end

class NaryRangeTree:
    def __init__(self):
        self.root = NaryRangeTreeNode(None, float("-inf"), float("inf"))

    def clear(self):
        self.root = NaryRangeTreeNode(None, float("-inf"), float("inf"))
        
    def insert(self, value, range_start, range_end):
        new_node = NaryRangeTreeNode(value, range_start, range_end)
        self._insert_recursive(self.root, new_node)
                    
    def _insert_recursive(self, current_node, new_node):
        children = current_node.children
        addedAsRoot = False
        i = 0
        #print("Current children:", [child.value for child in children])
        while i < len(children):
            child = children[i]
            #print(f"Checking {new_node.value} against {child.value}")
            # check for overlap (invalid)
            if self._has_overlap(child, new_node.range_start, new_node.range_end):
                raise OverlappingSkills(new_node.value, new_node.range_start, new_node.range_end, child.value, child.range_start, child.range_end)
            # node less than current node
            elif new_node.range_start < child.range_start and new_node.range_end <= child.range_start:
                #print("Node less than current node")
                children.insert(i, new_node)
                
                return
            # node should be child of root node
            elif new_node.range_start >= child.range_start and new_node.range_end <= child.range_end:
                if type(child.value) is ActionUnit:
                    raise ActionHasChildren(child.value.name)
                #print("Node should be child of root node")
                self._insert_recursive(child, new_node)
                return
            # node should be new root node
            if new_node.range_start <= child.range_start and new_node.range_end >= child.range_end:
                if type(new_node.value) is ActionUnit:
                    raise ActionHasChildren(new_node.value.name)
                #print("Node should be new root node")
                # If we hit this once already, hitting it again would add duplicates!
                old_child = children.pop(i)
                if not addedAsRoot:
                    children.insert(i, new_node)
                    i+=1
                addedAsRoot = True
                # TODO: change to rerun insert?
                new_node.children.append(old_child)
                # do NOT return here- there may be more children to move
            else:
                i+=1
                #print("Other case??")
        
        #node greater than all other nodes
        if not addedAsRoot:
            #print("Node greater than all other nodes. Appending")
            children.append(new_node)
            

    def _has_overlap(self, node, range_start, range_end):
        # TODO: Handle singles
        if (node.range_start < range_start and node.range_end > range_start and node.range_end < range_end) or \
            (node.range_start > range_start and node.range_start < range_end and node.range_end > range_end):
            #or (node.range_start == range_start and node.range_end == range_end):
            return True
        return False
    
    def get(self, value):
        result = self._retrieve_recursive(self.root, value, popValue = False)
        if result:
            return result
        else:
            raise ValueError(f"Node with value {value} not found.")
    
    def pop(self, value):
        result = self._retrieve_recursive(self.root, value, popValue = True)
        print("Result:", result)
        if result:
            return result
        else:
            raise ValueError(f"Node with value {value} not found.")
    
    def _retrieve_recursive(self, current_node, value, popValue = False):
        children = current_node.children
        found_value = None
        # if current_node.value:
        #    print("Level:", current_node.value.name, current_node.value.frame_start, current_node.value.frame_end)
        for i,child in enumerate(children):
            #print(child.value.uuid,child.value.name,child.value.frame_start,child.value.frame_end)
            if (callable(value) and value(child.value)) \
                or (not callable(value) and value and child.value == value):
                #print("Found")
                if popValue:
                    found_child = children.pop(i)
                    dangling_children = found_child.children
                    #print("Dangling children",dangling_children)
                    if dangling_children:
                        initPosition = i
                        while dangling_children:
                            #print("Inserting dangling child",initPosition)
                            children.insert(initPosition, dangling_children.pop())
                            print(children)
                else:
                    found_child = children[i]
                return found_child
            else:
                found_value = self._retrieve_recursive(child, value, popValue)
                #print(f"Exiting level {child.value.name}", found_value)
            # If found_value, exit
            if found_value:
                return found_value
        return found_value
    
    def query_value_with_tightest_range_containing(self, num_in_range):
        return self._query_tightest_range_containing_recursive(self.root, num_in_range)
    
    def _query_tightest_range_containing_recursive(self, current_node, num_in_range):
        children = current_node.children
        current_best_node = current_node
        
        for child in children:
            if child.range_start <= num_in_range and child.range_end >= num_in_range:
                return self._query_tightest_range_containing_recursive(child, num_in_range)
            
        return current_best_node
    
    def loose_range_query(self, range_start, range_end):
        result = []
        self._loose_range_query_recursive(self.root, range_start, range_end, result)
        return result

    def _loose_range_query_recursive(self, current_node, range_start, range_end, result):
        if (range_start <= current_node.range_start and  current_node.range_start <= range_end) \
            or (range_start <= current_node.range_end and current_node.range_end <= range_end):
            result.append(current_node.value)
        for child in current_node.children:
            self._loose_range_query_recursive(child, range_start, range_end, result)

    def traverse(self, levels = False):
        nodes = []
        if levels:
            self._traverse_recursive(self.root, nodes, 0)
        else:
            self._traverse_recursive(self.root, nodes, -1)
        return nodes[1:]

    def _traverse_recursive(self, current_node, nodes, level):
        if level >= 0:
            nodes.append((current_node, level))
        else:
            nodes.append(current_node)
        for child in current_node.children:
            self._traverse_recursive(child, nodes, level+1 if level >= 0 else -1)

# New NaryRangeTree tests
class Overlap(unittest.TestCase):
    # Test prevention of overlapping nodes
    def test(self):
        tree = NaryRangeTree()
        tree.insert("A", 3, 5)
        
        for start in range (0,2+1):
            for end in range(4, 4+1):
                with self.assertRaises(OverlappingSkills, msg = f"{start},{end}"):
                    tree.insert("ERR", start, end)
        
        for start in range(4, 4):
            for end in range(6, 10):
                with self.assertRaises(OverlappingSkills, msg = f"{start},{end}"):
                    tree.insert("ERR", start, end)     
                         
class InsertionDeletionProperLocations(unittest.TestCase):
    # Test insertion and deletion of nodes into the tree
    def test(self):
        tree = NaryRangeTree()
        
        # Insert nodes
        tree.insert("A", 0, 10)
        tree.insert("B", 4, 5)
        tree.insert("B2", 5, 10)
        tree.insert("C", 10, 11)
        tree.insert("D", 1,2)
        tree.insert("E", 0, 20)
        
        print(tree.traverse())
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("A",0,10), 2, 0)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B",4,5), 3, 1)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B2",5,10), 3, 2)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("C",10,11), 2, 1)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("D",1,2), 3, 0)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("E",0,20), 1, 0)
        
        # Delete nodes
        tree.pop("D")
        TestMethods.assertMissing(self, tree, NaryRangeTreeNode("D",1,2))
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B",4,5), 3, 0)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B2",5,10), 3, 1)
        
        tree.pop("E")
        TestMethods.assertMissing(self, tree, NaryRangeTreeNode("E",0,20))
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("A",0,10), 1, 0)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B",4,5), 2, 0)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B2",5,10), 2, 1)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("C",10,11), 1, 1)
        
        tree.pop("A")
        TestMethods.assertMissing(self, tree, NaryRangeTreeNode("A",0,10))
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B",4,5), 1, 0)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("B2",5,10), 1, 1)
        TestMethods.assertLocation(self, tree, NaryRangeTreeNode("C",10,11), 1, 2)
        
class NoActionChildren(unittest.TestCase):
    # Test that an action node cannot have children
    def test(self):
        tree = NaryRangeTree()
        
        action_node = ActionUnit("uuid1","A", 0, 10)
        tree.insert(action_node, 0, 10)
        
        action_node_2 = ActionUnit("uuid2","B", 4, 5)
        with self.assertRaises(ActionHasChildren):
            tree.insert(action_node_2, action_node_2.frame_start, action_node_2.frame_end)
            
        action_node_3 = ActionUnit("uuid3","C", 0, 11)
        with self.assertRaises(ActionHasChildren) :
            tree.insert(action_node_3, action_node_3.frame_start, action_node_3.frame_end)
            
        skill_node_1 = SkillUnit("uuid4","D", 0, 20)
        tree.insert(skill_node_1, skill_node_1.frame_start, skill_node_1.frame_end)
        
        action_node_4 = ActionUnit("uuid5","E", 10, 12)
        tree.insert(action_node_4, action_node_4.frame_start, action_node_4.frame_end)
        
        skill_node_2 = ActionUnit("uuid6","F", 0, 4)
        with self.assertRaises(ActionHasChildren):
            tree.insert(skill_node_2, skill_node_2.frame_start, skill_node_2.frame_end)
            
        action_node_5 = ActionUnit("uuid7","G", 0, 30)
        with self.assertRaises(ActionHasChildren):
            tree.insert(action_node_5, action_node_5.frame_start, action_node_5.frame_end)
        
        
           
class TestMethods():
    def _traverse_recursive(test: unittest.TestCase, current_node, current_level, node, level, index):
            found_match = False
            for i,child in enumerate(current_node.children):
                # print(i,child,current_level)
                if child == node:
                    is_correct_location = i == index and current_level==level
                    test.assertTrue(is_correct_location, f"Expected node {node} to be at level {level} and index {index}. Was at level {current_level} and index {i}.")
                    if is_correct_location:
                        return True
                    else:
                        return False
                else:
                    found_match = TestMethods._traverse_recursive(test, child, current_level+1, node, level, index)
                    if found_match:
                        return True
                           
    def assertLocation(test: unittest.TestCase, tree: NaryRangeTree, node, level, index):
        if (TestMethods._traverse_recursive(test, tree.root, 1, node, level, index)):
            return True
        else:
            test.fail(f"Node {node} could not be found in the tree.")
            
    def assertMissing(test: unittest.TestCase, tree: NaryRangeTree, node):
        try:
            tree.get(node)
            test.fail(f"Node {node} was found in the tree.")
        except ValueError:
            return True
            
# Run Tests
if __name__ == "__main__":
    unittest.main()