
from collections import defaultdict
from dataclasses import dataclass
import pickle
from typing import Union, Tuple
from example_model.skill import StackItem
import numpy as np

@dataclass
class DataItem(StackItem):
    z_name: str 
    z_val: np.array
    term: bool
    #For debugging
    def __repr__(self) -> str:
        return '\n cnt:' +  str(self.counter)+' ' + \
               '\n call_fun:'+str(self.call_fun)+\
               '\n sub_fun:'+str(self.sub_fun)
                

class TrajDataset():
    """
    Parsing list of steps into dict of trajectories for each skill
    """
    def __init__(self) -> None:
        
        # Collection of functions
        self.func_dataset = defaultdict(list)
        
        # Stack for parsing trajectories
        # We need to get return values (z) for the fucntion if counter > 1. i.e to update current observation
        self.stack = []

        # All trajectories go here
        self.traj = defaultdict(list)

        #X - (call_fun, call_arg, counter) 
        #Y - (sub_fun,  sub_arg,  ret_val)
        #Z - (call_fun, ret_val) - basically a new abservation at t+1 
        #Term - (terminal,) 
    
    def to_name(self,fun:callable) -> Union[str, None]:
        """ Get name of the function """
        if fun is None:
            return None
        else: return fun.__name__
   
    def create_data_item(self, stack_item:StackItem, z:Union[tuple,None] = None) -> dict:
        """ Create a data point with X,Y,Z params """
        item = DataItem(call_fun=self.to_name(stack_item.call_fun),
                        call_arg=stack_item.call_arg,
                        sub_fun=self.to_name(stack_item.sub_fun),
                        sub_arg=stack_item.sub_arg,
                        ret_val=stack_item.ret_val,
                        counter=stack_item.counter,
                        term=stack_item.ret_val is not None,
                        z_name=self.to_name(z[0]) if z is not None else None,
                        z_val=z[1] if z is not None else None,
        )
        return item
    
    def add_new(self,stack_item:StackItem) -> None:
        """ Add new stack item to the func_dataset """
        # To make sure that all dp - datapoints have the same consistent structure
        z = None
        # When stack is not empty we need to update z for updating current observation
        if (len(self.stack) > 0):
            z = self.stack.pop() 
            z = (z.call_fun, z.ret_val)
        item = self.create_data_item(stack_item,z=z)
        self.func_dataset[self.to_name(stack_item.call_fun)].append(item)

    def finish(self,stack_item:StackItem)-> None:
        """ Finish trajectory and to the dataset """
        #First add a dp to the func_dataset
        self.add_new(stack_item)
        #Push new obs on the stack
        self.stack.append(stack_item)
        #Finalize trajectory
        traj =  [*self.func_dataset[self.to_name(stack_item.call_fun)]] 
        #Append new trajectory to approppriate key:val
        self.traj[self.to_name(stack_item.call_fun)].append(traj)
        #Empty trajectory
        self.func_dataset[self.to_name(stack_item.call_fun)] = []
        

    def save(self,name:str) -> None:
        with open(f'{name}.pickle', 'wb') as handle:
            to_save = {'traj':self.traj,'fun_map':self.fun_map}
            pickle.dump(to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
    def load_multiple(self,files:list) -> Tuple[dict,dict]:
        self.traj = defaultdict(list)
        self.fun_map = None
        for file in files:
            dataset, fun_map = self.load(file)
            if self.fun_map is  None:
                self.fun_map = fun_map

            for key,value in dataset.items():
                for subtraj in dataset[key]:
                    self.traj[key].append(subtraj)

        
        return self.traj, fun_map

    def load(self,name:str) -> Tuple[dict,dict]:
        with open(f'{name}.pickle', 'rb') as handle:
            
            to_load = pickle.load(handle)
            traj = to_load['traj']
            fun_map = to_load['fun_map']

            if 'term' not in fun_map:
                fun_map['term'] = len(fun_map)

            return traj, fun_map
           
    def parse(self,dataset:list[StackItem])-> None:
        # Go through all items in dataset
        for i in dataset:
            # If an item does not have return value we create a new trajectory 
            if i.ret_val is None:
                self.add_new(i)
            else:
            # If an item has return value we finalize a trajectory
                self.finish(i)

        # Function mapping
        self.make_dummy()
    
    def make_dummy(self,)-> None:
        self.fun_map = {}
        for id,key in enumerate(self.func_dataset.keys()):
            self.fun_map[key] = id 
        self.fun_map['term'] = len(self.fun_map)