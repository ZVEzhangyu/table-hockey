# here lies an example of how to train an RL agent on individual subgame


import argparse
import datetime
import numpy as np
import os
from pathlib import Path
import sys
import math
from pygame.math import Vector2
base_dir = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(base_dir)
engine_path = os.path.join(base_dir, "olympics_engine")
sys.path.append(engine_path)

import random

from olympics_engine.generator import create_scenario
from train.log_path import *

from olympics_engine.scenario import table_hockey
from olympics_engine.agent import *
ball_forward = 0

def findcenter(obs,number):
    if number in [8,10]:
        return Vector2(31.5, 19.5)
    x = np.argwhere(obs==number)
    mean_obs = np.mean(x, axis= 0)
    center = Vector2(mean_obs[0],mean_obs[1])
    return center

def get_heading(velocity:Vector2):
    heading = math.degrees(math.atan2(velocity.y, -velocity.x))
    return heading

def action_env(y, power, result):
    game_name = 'table-hockey'
    Gamemap = create_scenario(game_name)
    env = table_hockey(Gamemap)
    env.max_step = 500
    RENDER = True #显示画面改成True
    global ball_forward
    ball_forward = 0
    ctrl_agent_index = 0
    state = env.reset()
    env.agent_init_pos[2][1] = y
    env.agent_init_pos[1][1] = 200
    env.agent_init_pos[1][0] = 700
    if isinstance(state[ctrl_agent_index], type({})):
            obs_ctrl_agent, energy_ctrl_agent = state[ctrl_agent_index]['agent_obs'], env.agent_list[ctrl_agent_index].energy
    else:
        obs_ctrl_agent, energy_ctrl_agent = state[ctrl_agent_index], env.agent_list[ctrl_agent_index].energy
    if RENDER:
        env.render()
    step = 0
    while True:
        action_opp = [0,0]
        if step<6:
            action_ctl = [200,0]
        elif step<14:
            action_ctl = [0,0]
        elif step<17:
            if ball_forward==0:
                center_my = findcenter(obs_ctrl_agent, 10)
                center_ball = findcenter(obs_ctrl_agent, 2)
                ball_pose = center_ball - center_my
                ball_degree0 = get_heading(ball_pose)
                if ball_degree0<0:
                    ball_forward = -1 #区分球在视野左边还是右边
                else:
                    ball_forward = 1
            action_ctl = [0,ball_forward*30]
        elif step<22:# 第23步开始调整力度
            action_ctl = [power,0] #测试力是否可以击中球门
        elif step<25:
            action_ctl = [0,0]
        action = [action_ctl, action_opp]
        next_state, reward, done, _ = env.step(action)
        if isinstance(next_state[ctrl_agent_index], type({})):
                next_obs_ctrl_agent, next_energy_ctrl_agent = next_state[ctrl_agent_index]['agent_obs'], env.agent_list[ctrl_agent_index].energy
        else:
            next_obs_ctrl_agent, next_energy_ctrl_agent = next_state[ctrl_agent_index], env.agent_list[ctrl_agent_index].energy
        obs_ctrl_agent = next_obs_ctrl_agent

        step += 1
        if RENDER:
            env.render()
        if done:
            if step<90:
                result.append([center_ball, power]) #暂定游戏步数少于90算一脚进球门
            else:
                result.append(False)
            break
        if step>120:
            result.append(False)
            break
    return result

if __name__=='__main__':
    thread_num = 20
    
    from multiprocessing import Array, Process, Manager
    manager = Manager() 
    # 多进程进行打表操作
    ans = []
    agent = []
    # for k in range(201):
    #     y = 300+k
    #     for i in range(int(200/thread_num)):
    #         return_list = manager.list()
    #         for j in range(thread_num):
    #             p = Process(target=action_env,args=(y, i*thread_num+j, return_list, ))
    #             p.start()
    #             agent.append(p)
    #         for a in agent:
    #             a.join()
    #         for rl in return_list:
    #             if rl != False:
    #                 ans.append({'location':y,'obs':rl[0],'power':rl[1]})
    # np.save('./log.npy',ans)
    # 测试
    s = -1
    e = -1
    flag = 0
    ans = np.load('./log.npy',allow_pickle=True)
    tmp_ans = []
    for i in range(len(ans)):
        power = ans[i]['power']
        location = ans[i]['location']
        tmp_ans = action_env(location, power, tmp_ans)