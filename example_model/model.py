from time import sleep
import numpy as np
from example_model.basemodel import *
from typing import Union

MAX_CNT = 100
SLEEP_TIME = 0.1

class BaseAgentPolicy():    
    def __init__(self) -> None:
        raise 'Not implemented'

def ModelWrapper(cls:BaseAgentPolicy,fun:callable,model:Union[Model,callable])-> callable:
    """
    1-step prediction function
    """
    def wrapped(x:np.ndarray) -> callable:
        assert type(x) is np.ndarray
        pred_fun, pred_args = model.predict(cnt=1,x=x,z=None)
        sleep(SLEEP_TIME)

        for dict_vals in cls.__dict__:
            if dict_vals == pred_fun:
                call_fun = getattr(cls, dict_vals)
                return call_fun(pred_args)
    wrapped.__name__ = fun.__name__
    return wrapped

def WhileModelWrapper(cls:BaseAgentPolicy,fun:callable,model:Union[Model,callable])-> callable:
    """
    Multi-step prediction wrapper-function
    """
    def wrapped(x:np.ndarray):
        assert type(x) is np.ndarray

        # Init values
        pred_fun,z,cnt = (None, None, 1)

        while (pred_fun != 'term') and cnt <= MAX_CNT:
            sleep(SLEEP_TIME)
            pred_fun, pred_args = model.predict(cnt=cnt,x=x,z=z)
            for fun_name in cls.__dict__:
                if fun_name == pred_fun:
                    call_fun = getattr(cls, fun_name)

                    z = call_fun(pred_args)
            cnt += 1
        return pred_args
    wrapped.__name__ = fun.__name__
    return wrapped