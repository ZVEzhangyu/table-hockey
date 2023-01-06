import numpy as np
from pygame.math import Vector2
import math

def get_heading(velocity:Vector2):
    heading = math.degrees(math.atan2(velocity.y, -velocity.x))
    return heading

def find_door(obs, number):
    center_my = findcenter(obs,number)
    ans = None
    dis = 1000
    for i in range(40):
        for j in range(40):
            if obs[i][j]==7:
                center_other = Vector2(i,j)
                tmp_dis  = np.sqrt((center_my.x-center_other.x)**2 + (center_my.y-center_other.y)**2)
                if tmp_dis < dis:
                    dis = tmp_dis
                    ans = center_other
    return ans

def door_way(obs,controled_player_idx):
    idx_to_enemy_color = [10, 8]
    my_color = idx_to_enemy_color[controled_player_idx]
    center_my = findcenter(obs, my_color)
    center_door = findcenter(obs, 7)
    door_pose = center_door - center_my
    door_degree = get_heading(door_pose)
    if 60>door_degree>20:
        power = 100
    elif 150<door_degree<210:
        power = -100
    else:
        power = 0
    return power

def attack_ball(obs, degree, controled_player_idx):
    idx_to_enemy_color = [10, 8]
    my_color = idx_to_enemy_color[controled_player_idx]
    center_my = findcenter(obs, my_color)
    center_ball = findcenter(obs, 2)
    ball_pose = center_ball - center_my
    ball_degree = get_heading(ball_pose)
    ball_degree0 = (ball_degree + degree + 360)%360
    my_degree = ball_degree
    tmp_x = get_dis(obs,my_color)
    if 90<=ball_degree0<=270:
        if 7 not in obs or tmp_x<20:
            if tmp_x>25:
                tmp_y = 8
            else:
                tmp_y = 6
            theta_run = math.degrees(math.atan2(tmp_y,tmp_x))
            if ball_degree0<180:
                ball_degree0 += theta_run
            else:
                ball_degree0 -= theta_run
            ball_degree = ball_degree0 - degree
        else:
            center_door = find_door(obs, 2)
            door_pose = center_door - center_my
            door_degree = get_heading(door_pose)
            
            ball_degree = 0.7*ball_degree+0.3*door_degree
            
        if abs(ball_degree)>30:
            ball_degree = 30*(ball_degree/abs(ball_degree))
        my_degree = ball_degree
        return [200, my_degree]

    if tmp_x>15:
        if 7 in obs:
            center_door = find_door(obs, 2)
            door_pose = center_door - center_my
            door_degree = get_heading(door_pose)
            my_degree = 0.8*ball_degree+0.2*door_degree
        else:
            if tmp_x>30:
                tmp_y = 8
            else:
                tmp_y = 6
            theta_run = math.degrees(math.atan2(tmp_y,tmp_x))
            if ball_degree0<60:
                ball_degree0 += theta_run
            else:
                ball_degree0 -= theta_run
            my_degree = ball_degree0 - degree
    else:
        if 7 in obs:
            center_door = find_door(obs, 2)
            door_pose = center_door - center_my
            door_degree = get_heading(door_pose)
            my_degree = 0.9*ball_degree+0.1*door_degree
    if abs(my_degree)>30:
        my_degree = 30*(my_degree/abs(my_degree))
    return [100,my_degree]

ball_forward = 0
power = 800
flag = 100
flag_first_shot = 0
dis_first_shot = 100
def first_shot(obs_ctrl_agent,controled_player_idx,count_turn,index_list,ans,degree):
    global ball_forward
    global power
    global flag
    global dis_first_shot
    global flag_first_shot
    if count_turn<6:
        action_ctl = [200, 0]
    elif count_turn<14:
        action_ctl = [0, 0]
    elif count_turn<17:
        if ball_forward==0:
            idx_to_enemy_color = [10, 8]
            my_color = idx_to_enemy_color[controled_player_idx]
            center_my = findcenter(obs_ctrl_agent, my_color)
            center_ball = findcenter(obs_ctrl_agent, 2)
            ball_pose = center_ball - center_my
            for i in range(len(index_list)):
                if abs(center_ball.y-index_list[i])<flag:
                        flag = abs(center_ball.y-index_list[i])
                        power = ans[i]
            ball_degree0 = get_heading(ball_pose)
            if ball_degree0<0:
                ball_forward = -1
            else:
                ball_forward = 1
        action_ctl = [0,ball_forward*30]
    elif count_turn<22:
        action_ctl = [power,0]
    elif count_turn<25:
        action_ctl = [0,-ball_forward*30]
    else:
        idx_to_enemy_color = [10, 8]
        my_color = idx_to_enemy_color[controled_player_idx]
        if get_dis(obs_ctrl_agent,my_color)<dis_first_shot and flag_first_shot==0:
                dis_first_shot = get_dis(obs_ctrl_agent,my_color)
                action_ctl = [0,0]
        else:
            flag_first_shot = 1
            if 2 in obs_ctrl_agent:
                action_ctl = attack_ball(obs_ctrl_agent,degree,controled_player_idx)
            else:
                action_ctl = [0,30]
    return [[action_ctl[0]],[action_ctl[1]]]
            
def findcenter(obs,number):
    if number in [8,10]:
        return Vector2(31.5, 19.5)
    x = np.argwhere(obs==number)
    mean_obs = np.mean(x, axis= 0)
    center = Vector2(mean_obs[0],mean_obs[1])
    return center

def get_dis(obs,num):
    center_my = findcenter(obs,num)
    center_other = findcenter(obs,2)
    dis  = np.sqrt((center_my.x-center_other.x)**2 + (center_my.y-center_other.y)**2)
    return dis

degree0 = 0
degree1 = 0
count_num = 0

def my_controller(observation, action_space, is_act_continuous=False):
    action_mask = [1 for i in range(36)]
    action_mask[30:] = [0 for i in range(36-30) ]
    agent_action = [[0],[0]]
    global degree0
    global degree1
    global count_num
    import os
    cur_path = os.path.dirname(__file__)
    model_actor_path = os.path.join(cur_path, 'ans.json')
    import json
    f = open(model_actor_path, 'r')
    content = f.read()
    a = json.loads(content)
    index_list = a['index_list']
    ans = a['ans']
    f.close()
    obs = observation['obs']['agent_obs']
    ctrl_agent_index = observation['controlled_player_index']
    if ctrl_agent_index==0:
        degree = degree0
    else:
        degree = degree1
    # if ctrl_agent_index==1:
    #     agent_action = [[0],[30]]
    #     # if 2 in obs:
    #     #     agent_action= attack_ball(obs, degree,ctrl_agent_index)
    #     #     agent_action = [[agent_action[0]],[agent_action[1]]]
    # else:
    agent_action = first_shot(obs,ctrl_agent_index,count_num,index_list,ans,degree)
    count_num += 1
    
    
    if ctrl_agent_index==0:
        degree0 += agent_action[1][0]
        degree0 = (360+degree0)%360
    else:
        degree1 += agent_action[1][0]
        degree1 = (360+degree1)%360
        
    return agent_action