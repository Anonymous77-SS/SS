from sklearn.ensemble import RandomForestClassifier
import numpy as np
from typing import Union

IdentityModel = lambda x: x

class Model():
    """
    BaseModel class
    """
    def __init__(self,fun_map:dict,func:callable) -> None:
        self.x=[]
        self.y=[]
        # str:idx
        self.fun_map = fun_map
        # skill name
        self.name = func
        # inverse map from idx:str
        self.inv_fun_map = dict(zip(fun_map.values(),fun_map.keys()))

        #X - (call_fun,call_arg,counter) 
        #Z - (return value from a sub_function)
        #Y - (sub_fun,ret_val)
        #Term - (terminal,)

    def fit(self, all_trajs:list,)-> None:
        """
        Collecting all dp and fit a Skill
        """
        #(x,z,cnt) - > f, f_args
        for traj in all_trajs:
            for step in traj:
                x = step.call_arg
                cnt = step.counter
                ## Maybe better do concatenation

                ## in case if we updated observation
                if step.z_name is not None:
                    z = step.z_val 
                    # x = z
                
                ## if we did not update observation
                else:
                    z = None

                x = self.process_xz(np.array(x),z)

                self.x.append((np.array(x).reshape(-1,)*cnt))

                ## If terminal function
                if step.term:
                    self.y.append(self.fun_map['term'])
                else:
                    self.y.append(self.fun_map[step.sub_fun])

        self.clf = RandomForestClassifier()
        self.clf.fit(self.x,self.y) 
    
    def process_xz(self,x:np.ndarray,z:np.ndarray=None)-> np.ndarray:
        if z is None:
            z = np.zeros_like(x)
        else:
            z = z.reshape(x.shape)
        x=np.concatenate([x,z])
        return x
    
    def predict(self,cnt:int=1,x:np.ndarray=None,z:np.ndarray=None)-> Union[str,np.ndarray]:
        x_ = self.process_xz(x,z)
        x_ = x_ * cnt
        x_ = x_.reshape(1,-1)
        y = self.clf.predict(x_)
        y = self.inv_fun_map[y[0]]
        return y, z if z is not None else x