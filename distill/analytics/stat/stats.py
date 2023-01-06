#
# Copyright 2022 The Applied Research Laboratory for Intelligence and Security (ARLIS)
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


### TODO: convert into usable function 

import sys
sys.path.append('../')

import datetime
#import distill
import json
#import networkx as nx
import os
#import pandas as pd
#import plotly.express as px
import re

# setup to convert JSON to required format for segmentation
def filtered_setup(file, date_type):
    
    with open(file) as json_file:
            raw_data = json.load(json_file)

    # filter
    filtered_data = []        

    for log in raw_data:
        # filter for dict items 
        if isinstance(log, bool) == 0:
            if log['type'] == 'click':
                if log['logType'] == 'raw': # 
                    filtered_data.append(log)
                    
    data = {}
    for log in filtered_data:
            # UUID = sessionID + clientTime + logType + type
            data[distill.getUUID(log)] = log

    for uid in data:
        # get the log
        log = data[uid]
        # get log's clientTime
        client_time = log['clientTime']
        # convert the log's datetime
        if date_type == "integer":
            log['clientTime'] = distill.epoch_to_datetime(client_time)
        elif date_type == "datetime":
            log['clientTime'] = pd.to_datetime(client_time, unit='ms', origin='unix')

    # Sort data based off clientTime, return dict
    sorted_data = sorted(data.items(), key=lambda kv: kv[1]['clientTime'])
    sorted_dict = dict(sorted_data)

    return (sorted_data, sorted_dict)     


# clickrate function passed formatted data 
def session_clickrate(file, date_type):
    
    print("File: "+ file)
    data_many_session = filtered_setup(file, "datetime")
    sorted_dict = data_many_session[1]
    segs = distill.Segments([]) # --> [] 
    ##segments = distill.create_segment(sorted_dict, segs.segment_name, segs.get_start_end_val) # other create call
    print(segs)

    # get session id's from dict
    session_ids = sorted(distill.find_meta_values('sessionID', sorted_dict), key=lambda sessionID: sessionID)
    # for each id, generate segment object 
    for session_id in session_ids:
        segs.append_segments(distill.generate_collapsing_window_segments(sorted_dict, 'sessionID', [session_id], session_id))  

    # improve readability of Segment names
    for index in range(len(segs)):
        segs[index].segment_name = "Session" + str(index)   

    for segment in segs:
        # convert time to sec before diving by num logs 
        totalTime = (segment.get_start_end_val()[1] - segment.get_start_end_val()[0]).total_seconds()
        clickRate = segment.get_num_logs() / totalTime
        #print("Clickrate: " + str(round(clickRate,2)) + " clicks/second")
        print(segment.get_segment_name() + " -> Start: " + str(segment.get_start_end_val()[0]) + 
              " End: " + str(segment.get_start_end_val()[1]) + "\nTotal time to complete: " + str(round(totalTime,1)) + 
              " seconds\nClickrate: " + str(round(clickRate,2)) + " clicks/second")


### PREVIOUS CODE ###

# # Session Click-Rate
# def session_clickrate_dict(data, session):
#     """
#     Creates clickrate dictionary from user defined dataframe and session
#     :param data: Dataframe of logs imported from JSON (SampleLogs2Session)
#     :param session: String of session ID of interest
#     :return: A session clickrate dictionary
#     """

#     # turn clientTime into indexable data-time object
#     new_dateTime = pd.to_datetime(df['clientTime'], unit='ms', origin='unix')
#     df['client_dateTime'] = (new_dateTime - pd.Timestamp('1970-01-01')) // pd.Timedelta('1ms')
#     df.set_index('client_dateTime', inplace=True)
#     df.sort_values('client_dateTime')
#     print('data indexed by time')

#     if session != False:
#         # filter data by session
#         session_segment = (df.groupby(df['sessionID'])).get_group(session)
#         print('data filtered')

#     # segmentation
#     # build filter mask
#     # filter rows Events Of Interest (eoi)
#     # create list of tuplesthat bound start/stop of each segment
#     eoi = ['XMLHttpRequest.open', 'XMLHttpRequest.response']
#     segment_events = session_segment.loc[session_segment['type'].isin(eoi)]
#     segment_events = segment_events.sort_values('client_dateTime').index
#     segment_start_stop = pairwiseStag(segment_events)
#     print('segments defined')

#     cr_dict = {}
#     for i in segment_start_stop:
#         segnum = 'Segment' + str(segment_start_stop.index(i) + 1)
#         cr_dict[segnum] = {}
#         cr_dict[segnum]['Segment'] = str(segnum)
#         cr_dict[segnum]['Start_stop'] = i
#         cr_dict[segnum]['Duration_ms'] = i[1] - i[0]
#         dur_sec = ((i[1] - i[0]) / 1000)
#         cr_dict[segnum]['Duration_s'] = dur_sec

#         tempdf = session_segment.reset_index()
#         segmentClicks = len(tempdf.query('clientTime >= @i[0] & clientTime <= @i[1] & type == "click"').index)
#         cr_dict[segnum]['Clicks_c'] = segmentClicks
#         cr_dict[segnum]['Clickrate_cs'] = round(segmentClicks / dur_sec, 3)

#     return cr_dict
