import sys
sys.path.append('../')
import os
import pandas as pd
import json
import distill


def ingest_data():
    def get_file_paths(directory_path):
        path_list = []
        for root, directories, files in os.walk(directory_path):
            for file in files:
                # Different workflow needed for Amir next time
                if file != "logs_nome_amir.json":
                    path = os.path.join(root, file)
                    path_list.append(path)
        return path_list

    def convert_time(date_type, client_time):
        if date_type == "integer":
            return distill.epoch_to_datetime(client_time)
        elif date_type == "datetime":
            return pd.to_datetime(client_time, unit='ms', origin='unix')
        else:
            return client_time

    # load json into our formatted dict
    def setup(file, date_type):
        with open(file, 'r', encoding='utf-8') as json_file:
            raw_data = json.load(json_file)

        # Data = {sessionID : {logUUID : log}}
        data = {}
        curr_sess = {}
        curr_id = next(iter(raw_data))['sessionID']
        # For each log of type 'visit' or 'click', attach it to the log's uuid in the curr_sess dictionary
        for log in raw_data:
            if 'type' in log and (log['type'] == 'visit') and ('name' in log['details']):
                # If the sessionID is different from before, attach the sorted curr_sess dictionary to the curr_id in data
                # and reset it
                if log['sessionID'] != curr_id:
                    data[curr_id] = dict(sorted(curr_sess.items(), key=lambda kv: kv[1]['clientTime']))
                    curr_id = log['sessionID']
                    curr_sess = {}
                # Convert clientTime to specified type and add it to the current session dictionary
                client_time = log['clientTime']
                log['clientTime'] = convert_time(date_type, client_time)
                curr_sess[distill.getUUID(log)] = log
        # Add the final session's dict to the data dict
        data[curr_id] = dict(sorted(curr_sess.items(), key=lambda kv: kv[1]['clientTime']))
        
        return data

    # Circumventing formatting issues to get all the paths
    liam_vlad_dir = (os.getcwd() + '/data3')
    liam_vlad = get_file_paths(liam_vlad_dir)
    all_paths = [path.replace("\\", "/") for path in liam_vlad]

    # Define all the log data files' names
    vlad_file = "data3/logs_nome_vlad.json"
    liam_file = "data3/logs_nome_liam.json"
    madeline_files = [path for path in all_paths if "madeline" in path]
    jason_files = [path for path in all_paths if "jason" in path]

    # Assemble Madeline's data into a dictionary from each of her files
    madeline_data = {}
    for file in madeline_files:
        if len(madeline_data) == 0:
            madeline_data = setup(file, "datetime")
        else:
            madeline_data.update( setup(file, "datetime") )

    # Assemble Jason's data into a dictionary from each of his files
    jason_data = {}
    for file in jason_files:
        if len(madeline_data) == 0:
            jason_data = setup(file, "datetime")
        else:
            jason_data.update( setup(file, "datetime") )

    # Create the overall data_dict = {sessionID: {logID: log}}
    data_dict = setup(vlad_file, "datetime")
    liam_data = setup(liam_file, "datetime")
    data_dict.update( liam_data )
    data_dict.update( madeline_data )
    data_dict.update( jason_data )

    return data_dict

def preprocess_data(data_dict):
    def generate_sublists(input_list):
        output_list = []
        n = len(input_list)

        for i in range(n):
            for j in range(i + 1, n + 1):
                sublist = input_list[i:j]
                if len(sublist) > 1:
                    output_list.append(sublist)

        return output_list

    # Compress the dense data_dict into the simpler sess_elements = {sessionID : [place1, place2, ...]}
    sess_elements = {}
    for sessID,logs in data_dict.items():
        # Dissect the logs and store them in the sess_elements dictionary
        for logID,log in logs.items():
            elem_name = log['details']['name']
            if (not sessID in sess_elements.keys()):
                sess_elements[sessID] = [ elem_name ]
            else:
                sess_elements[sessID] += [ elem_name ]


    # The smallest workflow we have is size 6, so anything less than that gets cut (if needed)
    data = [sess_elements[sessID] for sessID in sess_elements.keys() if len(sess_elements[sessID]) > 5]

    # Create inputs of various sizes for each session's workflow so it can understand the sequencing
    all_data = []
    for sess_lst in data:
        all_data += generate_sublists(sess_lst)

    # Finally, split each session's list into all elements before the last one (inputs) and the last one (output)
    data_tups = [(s[:-1], s[-1]) for s in all_data]
    df = pd.DataFrame(data_tups, columns=["inputs", "targets"])

    return df

if __name__ == "__main__":
    data_dict = ingest_data()
    df = preprocess_data(data_dict)
    print(df.head())