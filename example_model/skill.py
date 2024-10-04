from dataclasses import dataclass
from copy import copy
import functools
from typing import Union

GLOBALSTACK = []
DATASET = []

@dataclass
class StackItem:
    call_fun: callable # the current function
    call_arg: list  # called args to the function
    sub_fun: callable # the function that is being called
    sub_arg: list # subargs to the called function
    counter: int  # how many time steps are we being in the called function
    ret_val: int  # return value from the function
    
    #Helper fun
    def name(self,fun:callable) -> Union[str, None]:
        # if is str is there for sega upload
        if type(fun) is str:
            return fun
        if fun is not None:
            return fun.__name__
        else:
            return ''
        
    #For debugging
    def __repr__(self) -> str:
        return 'call_fun:'+str(self.name(self.call_fun))+\
            '\n sub_fun:'+str(self.name(self.sub_fun))+\
            '\n cnt:' +  str(self.counter)+\
            '\n ret_val:' + str(1 if self.ret_val is not None else 0)+\
            '\n call_arg: ' + str(1 if self.call_arg is not None else 0)+\
            '\n sub_arg: ' + str(1 if self.sub_arg is not None else 0) 

## Wrap around a function that is a skill
def Skill(func:callable) -> callable:
    @functools.wraps(func)  # Preserve metadata of the original function
    def wrapped(*args) -> callable:
        # First we check that global stack is not empty
        if len(GLOBALSTACK) != 0:
            # Modify the last item on the stack and add it to the dataset
            item = GLOBALSTACK[-1]
            item.sub_fun = func
            item.sub_arg = args
            item.counter += 1
            GLOBALSTACK[-1] = item
            # Have to use copy otherwise will have problems
            DATASET.append(copy(item))

        # If global stack is empty we skip adding data to dataset
        item = StackItem(call_fun=func,
                         call_arg=args,
                         sub_fun=None, # Since nothing on stack we don't know yet which function we are gonna call
                         sub_arg=None,
                         ret_val=None,
                         counter=0
                         )
        
        #Add function on global stack
        GLOBALSTACK.append(item)

        #Execute function
        res = func(*args)

        #Take an item from the stack
        last_stack_item = GLOBALSTACK.pop(-1)
        
        #Update return value and increase counter
        last_stack_item.ret_val = res 
        last_stack_item.counter += 1

        #Put the skill into dataset that is gonna be parsed
        DATASET.append(last_stack_item)
        return res
    
    # Update skill name
    wrapped.__name__ = func.__name__
    return wrapped