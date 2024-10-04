import inspect
import cv2
import gymnasium as gym
from example_model.convert import load_skillsega
from example_model.model import WhileModelWrapper
from example_model.skill import *
from example_model.basemodel import *
from example_model.dataset import *
import keyboard
from time import sleep
from minigrid.wrappers import RGBImgObsWrapper

env = RGBImgObsWrapper(gym.make("MiniGrid-DoorKey-5x5-v0", render_mode="human"))

class AgentPolicy():
    
    def __init__(self) -> None:
        pass

    def get_input():
        action = int(keyboard.read_key())
        sleep(0.5)
        return action
    
    def WhileNot(x):
        action = -1
        while action != 't':
            action = keyboard.read_key()
            sleep(0.5)
            #Elementary Actions
            if action=='a':
                x = AgentPolicy.turn_left()
            elif action =='d':
                x = AgentPolicy.turn_right()
            elif action =='w':
                x = AgentPolicy.move_forward()
            elif action =='e':
                x = AgentPolicy.pickup()
            elif action =='r':
                x = AgentPolicy.drop()
            elif action =='q':
                x = AgentPolicy.toggle()
            elif action =='n':
                x = AgentPolicy.done()
            elif action=='t':
                break
        return x

    @Skill
    def move_to(obs):
        print("move_to")
        return True

    @Skill
    def root(obs):
        print('root')
        x = AgentPolicy.WhileNot(obs)
        return True

    @Skill
    def unlock_door(obs):
        # pickups key and unlocks door
        obs = AgentPolicy.get_key(obs)
        obs = AgentPolicy.go_to_door(obs)
        return obs
    
    
    @Skill
    def get_key(arg):
        print('getting key to the door')
        x = AgentPolicy.WhileNot(obs)
        return True

    @Skill
    def go_to_door(arg):
        print('moving to door')
        x = AgentPolicy.WhileNot(obs)
        return True

    @Skill
    def move_forward(x=0):
        print("move_forward")
        env.step(2)
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
    @Skill
    def turn_left(x=0):
        print("turn left")
        env.step(0)
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
    @Skill
    def turn_right(x=0):
        print("turn right")
        env.step(1)
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
    @Skill
    def pickup(x=0):
        print("pickup")
        env.step(3)
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
    @Skill
    def drop(x=0):
        print("drop")
        env.step(4)
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
    @Skill
    def toggle(x=0):
        print("toggle")
        env.step(5)
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
    @Skill
    def done(x=0):
        env.step(6)
        print("done")
        return np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    
if __name__ == "__main__":
    def get_skills(obj):
        '''Returns an ordered dictionary of all skill functions and their method calls in the agent.'''
        skills = dict()
        for name in dir(obj):
            method = getattr(obj, name)
            if inspect.isfunction(method):
                if hasattr(method, '__wrapped__'):
                    skills[name] = method
        return skills

    print("Functions:")
    skills = get_skills(AgentPolicy)
    print(skills)
    
    data = load_skillsega("example_model/data/MiniGrid-DoorKey-5x5-v0_43.sega")
    for d in data:
        d.call_fun = skills[d.call_fun]
        d.sub_fun = None if d.sub_fun == '' else skills[d.sub_fun]
    
    
    # for _ in range(1):
    #     done = False
    #     # 
    #     obs,_ = env.reset()
    #     frame_rate = 1
    #     i = 0
    #     # action = AgentPolicy.root(obs)
    #     obs, rew, terminated, truncated, info = env.step(0)
    #     # 
    #     action = AgentPolicy.root(obs)
    #     obs, rew, terminated, truncated, info = env.step(action)
    #     done = terminated 
    # env.close()

    # for data in DATASET:
    #     print(data)
    #     print("=====")
    
    
    preproc_dataset = TrajDataset()
    #preproc_dataset.load_multiple([])

    ## In case of recording 
    # preproc_dataset.parse(DATASET)
    preproc_dataset.parse(data)
    
        
    models = defaultdict()
    for func in preproc_dataset.traj:
        print('FITTING',func)
        if func not in ('root','move_to','move_forward','turn_left','turn_right','get_key','go_to_door'):
            continue
        print('***************')
        model = Model(preproc_dataset.fun_map,func)
        model.fit(preproc_dataset.traj[func])
        models[func]= model
        print('-----------------')

    print('keys',models.keys())

    for key in models.keys():

        if key == AgentPolicy.root.__name__:
            new = WhileModelWrapper(AgentPolicy,AgentPolicy.root,models[key])
            print(new.__name__)
            print(key )
            AgentPolicy.root = new

        elif key == AgentPolicy.move_to.__name__:
            new = WhileModelWrapper(AgentPolicy,AgentPolicy.move_to,models[key])
            print(new.__name__)
            print(key )
            AgentPolicy.move_to = new
        
        elif key == AgentPolicy.go_to_door.__name__:
            new = WhileModelWrapper(AgentPolicy,AgentPolicy.go_to_door,models[key])
            print(new.__name__)
            print(key )
            AgentPolicy.go_to_door = new
        
        elif key == AgentPolicy.get_key.__name__:
            new = WhileModelWrapper(AgentPolicy,AgentPolicy.get_key,models[key])
            print(new.__name__)
            print(key )
            AgentPolicy.get_key = new

    print("TESTING")
    
    env = RGBImgObsWrapper(gym.make("MiniGrid-DoorKey-5x5-v0", render_mode="human"))
    done = False
    obs,_ = env.reset(seed=43)
    obs = np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    action = AgentPolicy.root(obs)
    obs = np.array(env.get_frame(highlight=True, tile_size=env.tile_size))
    print("Check image for success")
    env.close()
    # Save obs as image
    cv2.imwrite("sega_run.png", obs)