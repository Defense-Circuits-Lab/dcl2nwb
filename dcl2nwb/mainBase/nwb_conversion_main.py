from dcl2nwb.mainBase.base_func_sheet import *
from pynwb import NWBHDF5IO
import pandas as pd
import numpy as np
import os
from tkinter.filedialog import askdirectory
from datetime import datetime


in_dir = askdirectory(title='select the input root directory...')
name_ = in_dir.split('/')[-1]
time_ = datetime.now().strftime('%Y%m%d-%H%M%S')
root_name = f'{name_}-NWB-{time_}'
out_dir = os.path.join('/'.join(in_dir.split('/')[:-1]), root_name)  # to make a new tree just on the same level
os.mkdir(out_dir)  # make the new directory | can never be replaced or rewritten due to datatime component ;)

for root_, dir_, file_ in os.walk(in_dir):
    rel_path = os.path.relpath(root_, in_dir)
    curr_path = os.path.join(out_dir, rel_path)
    if rel_path != '.':
        os.mkdir(curr_path)  # copying the tree simultaneously
    if not any(dir_):
        # read in the main-info-sheet
        try:
            main_info_dict = pd.read_csv(os.path.join(root_, 'main-info-sheet.csv'), index_col='data/meta').to_dict()
        except NameError:
            raise ('couldn\'t find main-info-sheet.csv...\n'
                   'check your directories!')
        print(f'starting conversion of the session in directory:\n'
              f'{root_}')
        nwb_file = []  # to start with
        for key_ in main_info_dict.keys():
            pointer_ = main_info_dict[key_]
            for dum_ in list(pointer_.keys()):
                # some time there is no mainData and only metaData, try blocking to account for this
                try:
                    # to define absolute paths for each file (key)
                    pointer_.update({dum_: os.path.join(root_, pointer_[dum_])})
                except:
                    pass  # pass if the value is nan
            exec(f'nwb_file = {key_}(nwb_file, pointer_)')
        print('successfully converted...')
        # write it onto the file
        with NWBHDF5IO(os.path.join(curr_path, 'nwb-session-file.nwb'), 'w') as io:
            io.write(nwb_file)
        print(f'successfully written the session nwb file in the directory:\n'
              f'{curr_path}\n'
              f'###')

