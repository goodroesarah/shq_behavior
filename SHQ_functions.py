#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 17:03:37 2020

@author: sarahgoodroe
"""

## functions for SHQ VBM data (subset of levels)
import pandas as pd
import numpy as np
import json
#import matplotlib.pyplot as plt
import math
from glob import glob

## get values for all path integration levels 
## edit for old people paper
#flare_levels = [4,9,14,19,24,29,34,39,44,49,54,59,64,69,74]
path_levels = [1,6,8,11,16,43]
#radial_levels = [1,2,3,4,5]
#repeat_levels = 43 

## get distance travelled 
def get_euclidian():
    dist = 0
    for i in range(len(x)-1):
        p_dist = math.sqrt((x[i] - x[i+1])**2 + (y[i] - y[i+1])**2)
        dist += p_dist
        i += 1
    return dist

def get_path_int_values(path_id,out_path,sub_id):
    path_df = pd.DataFrame(columns = ['subID','level','complete','duration','map_view','distance','x','y','r'])
    row = 0
    global x
    global y
    for l in path_levels:
        if l > 8:
            path = glob(path_id + 'level0' + str(l) + '*')
        else:
            path = glob(path_id + 'level00' + str(l) + '*')
            
        with open(path[0]) as f:
            data = json.load(f)
            
        test = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))
        
        ##get trajectory information:
        traja = pd.DataFrame.from_dict(test.player.dropna())
        traja = traja.player.apply(pd.Series)
        x = np.array(5*traja.x)
        y = np.array(5*traja.y)
        r = np.array(5*traja.r)
        
        path_df.loc[row,'subID'] = sub_id
        path_df.loc[row,'level'] = l
        path_df.loc[row,'complete'] = test.meta.loc['early_termination']
        path_df.loc[row,'duration'] = test.meta.loc['duration']
        path_df.loc[row,'map_view'] = test.meta.loc['map_view_duration']
        path_df.loc[row,'distance'] = get_euclidian()
        path_df.loc[row,'x'] = x
        path_df.loc[row,'y'] = y
        path_df.loc[row,'r'] = r
        
        row += 1
        
    path_df.to_numpy()
    np.save(out_path + 'path/' + sub_id + '_path_levels.npy',path_df)

def get_flare_values(path_id,out_path,sub_id):
    flare_df = pd.DataFrame(columns = ['subID','level','complete','duration','flare_accuracy'])
    row = 0
    for l in flare_levels:
        if l > 9:
            path = glob(path_id + 'level0' + str(l) + '*')
        else:
            path = glob(path_id + 'level00' + str(l) + '*')
            
        with open(path[0]) as f:
            data = json.load(f)
            
        test = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))
        
        flare_df.loc[row,'subID'] = sub_id
        flare_df.loc[row,'level'] = l
        flare_df.loc[row,'complete'] = test.meta.loc['early_termination']
        flare_df.loc[row,'duration'] = test.meta.loc['duration']
        flare_df.loc[row,'flare_accuracy'] = test.meta.loc['flare_accuracy']
        
        row += 1
    flare_df.to_numpy()
    np.save(out_path + 'flare/' + sub_id + '_flare_levels.npy',flare_df)
    
def get_level_43(path_id,out_path,sub_id):
    repeat_df = pd.DataFrame(columns = ['subID','level','complete','duration','map_view','distance','x','y','r'])
    row = 0
    global x
    global y
    for i in range(1,4):
        path = glob(path_id + 'level043_attempt00' + str(i) + '*')
    
        with open(path[0]) as f:
            data = json.load(f)
            
        test = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))
        
        ##get trajectory information:
        traja = pd.DataFrame.from_dict(test.player.dropna())
        traja = traja.player.apply(pd.Series)
        x = np.array(5*traja.x)
        y = np.array(5*traja.y)
        r = np.array(5*traja.r)
        
        repeat_df.loc[row,'subID'] = sub_id
        repeat_df.loc[row,'level'] = 43
        repeat_df.loc[row,'complete'] = test.meta.loc['early_termination']
        repeat_df.loc[row,'duration'] = test.meta.loc['duration']
        repeat_df.loc[row,'map_view'] = test.meta.loc['map_view_duration']
        repeat_df.loc[row,'distance'] = get_euclidian()
        repeat_df.loc[row,'x'] = x
        repeat_df.loc[row,'y'] = y
        repeat_df.loc[row,'r'] = r
        
        row += 1
        
    repeat_df.to_numpy()
    np.save(out_path + 'repeat/' + sub_id + '_repeat_43.npy',repeat_df)
    
def get_radial_values(path_id,out_path,sub_id):
    radial_df = pd.DataFrame(columns = ['subID','level','complete','duration','distance','radial_tech','probe_error','wm_error','x','y','r'])
    row = 0
    global x
    global y
    for l in radial_levels:
        
        path = glob(path_id + 'radial_level00' + str(l) + '*')
            
        with open(path[0]) as f:
            data = json.load(f)
            
        test = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in data.items() ]))
        
        ##get trajectory information:
        traja = pd.DataFrame.from_dict(test.player.dropna())
        traja = traja.player.apply(pd.Series)
        x = np.array(5*traja.x)
        y = np.array(5*traja.y)
        r = np.array(5*traja.r)
        
        ##get error information (part 1 arms: 2,3,6; part 2 arms: 1,4,5), level 4 has fog and all arms are open
        events = test.events.dropna()
        events = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in events.items() ]))
        events = events.transpose()
        arms = list(events.section.where(events.type == 'radial_section').dropna(how='all'))
        
        ##probe error: part 1 arms in part 2
        p1_track = []
        p2_track = []
        part1,part2 = 1,0
        
        for a in arms:
            if part1 == 1:
                p1_track.append(a)
                if all(b in p1_track for b in [2,3,6]):
                    part1,part2 = 0,1
                    continue
            if part2 == 1:
                p2_track.append(a)
        
        probe_error = 0
        probe_error += p2_track.count(2) + p2_track.count(3) + p2_track.count(6)
        probe_error = probe_error / 2
            
        ##wm error (part 2 arms re-entered in part 2)
        wm_error = 0
        if p2_track.count(1) > 1:
            wm_error += p2_track.count(1) - 2
        if p2_track.count(4) > 1:
            wm_error += p2_track.count(4) - 2
        if p2_track.count(5) > 1:
            wm_error += p2_track.count(5) - 2   
        wm_error = wm_error/ 2
        
        radial_df.loc[row,'subID'] = sub_id
        radial_df.loc[row,'level'] = l
        radial_df.loc[row,'complete'] = test.meta.loc['early_termination']
        radial_df.loc[row,'duration'] = test.meta.loc['duration']
        radial_df.loc[row,'distance'] = get_euclidian()
        radial_df.loc[row,'radial_tech'] = test.meta.loc['radial_technique']
        radial_df.loc[row,'probe_error'] = probe_error
        radial_df.loc[row,'wm_error'] = wm_error
        radial_df.loc[row,'x'] = x
        radial_df.loc[row,'y'] = y
        radial_df.loc[row,'r'] = r
        
        
        row += 1
        
    radial_df.to_numpy()
    np.save(out_path + 'radial/' + sub_id + '_radial_levels.npy',radial_df)