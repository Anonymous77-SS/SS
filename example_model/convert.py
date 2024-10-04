from pathlib import Path
import pickle
from typing import List
import zipfile
import cv2

import numpy as np
from data_structure.naryrangetree import NaryRangeTree
from example_model.skill import StackItem


def load_image_frame(file_path,frame):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        # Read the image file from the ZIP
        with zip_ref.open(f"{frame}.png") as file:
            # Read the image data
            image_data = file.read()
            
            # Convert the image data to a NumPy array
            image_array = np.frombuffer(image_data, np.uint8)
            
            # Decode the image array into an OpenCV image
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image

def rescale(img):
    return img
    #return cv2.resize(img, (500, 500), interpolation=cv2.INTER_AREA)

def convert_skillhub_recursive(node: NaryRangeTree, path, root=False):
        stack = []

        if root:
            call_func_name = "root"
            # TODO: Set to first frame of video?
            call_arg_vals = None
        else:
            call_func_name = node.value.name
            call_arg_vals = rescale(load_image_frame(path, node.value.frame_start))

        step_num = 1
        sub_func_name = None
                
        if node.children:
            for child in node.children:
                if type(call_arg_vals) is type(None):
                    call_arg_vals = rescale(load_image_frame(path, child.value.frame_start))
                
                sub_arg_vals = rescale(load_image_frame(path, child.value.frame_start))
                
                sub_func_name = child.value.name
                sub_uuid = child.value.uuid
                node_dict = {
                    "counter": step_num,
                    "call_fun": call_func_name,
                    "call_arg": call_arg_vals,
                    "sub_fun": sub_func_name,
                    "sub_arg": sub_arg_vals,
                    "ret_val": None
                    }
                new_node = StackItem(**node_dict)
                stack.append(new_node)
                print("Recursing into:", sub_func_name, sub_uuid)
                stack += convert_skillhub_recursive(child, path)
                step_num += 1

        if not root:
            termination_frame = node.value.frame_end #+1
            ret_arg_vals = rescale(load_image_frame(path, termination_frame))
            print("All Frames:", termination_frame)
        elif step_num == 1:
            raise ValueError("Root node has no children")
        else:
            # TODO: set to last frame of video?
            ret_arg_vals = sub_arg_vals
    
        node_dict = {
            "counter": step_num,
            "call_fun": call_func_name,
            "call_arg": call_arg_vals,
            "sub_fun": "" if not node.children else sub_func_name,
            "sub_arg": None if not node.children else sub_arg_vals,
            "ret_val": ret_arg_vals
            }
        stack.append(StackItem(**node_dict))
                
        return stack
    

def load_skillsega(path):
    path = Path(path)

    with zipfile.ZipFile(path, 'r') as zipf:
        with zipf.open("skilltree.pkl") as file:
            naryrangetree = pickle.load(file)
    
    return convert_skillhub(path, naryrangetree)

def convert_skillhub(path: str, naryrangetree: NaryRangeTree):
    dataset: List[StackItem] = convert_skillhub_recursive(naryrangetree.root,path,True)
    
    print("Dataset:")
    for item in dataset:
        print(item)
        print("======================================")
        
    return dataset

        
if __name__ == "__main__":
    load_skillsega("trajectoryexample.sega")