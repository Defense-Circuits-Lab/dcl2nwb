from dcl2nwb.mainBase.base_func_sheet import *
from dcl2nwb.mainBase.integration_from_csv import drive_scan
from dcl2nwb.utilBase.session2csv import session2csv
from pynwb import NWBHDF5IO
import pandas as pd
import numpy as np
import os
import pathlib
import shutil
from pathlib import WindowsPath  # to evaluate from strings
from tkinter import *
from tkinter.filedialog import askdirectory, askopenfilename
from datetime import datetime


# color coding of the outprinted status
class TextColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# possibility to change inputs to make the best out of it by user!
break_loop = False  # initial value to start with
while not break_loop:
    now_ = datetime.now().strftime('%Y%m%d-%H%M%S')  # avoid same folder name in a while loop
    in_dir_path = askdirectory(title='select the root directory containing data...')
    in_dir_path = pathlib.Path(in_dir_path)
    #
    out_dir_path = askdirectory(title='select the folder to write conversions into...')
    # making the output folder
    root_name = f'NWBConversions-{now_}'
    out_dir_path = pathlib.Path(out_dir_path) / root_name
    # make the new directory | can never be replaced or rewritten due to datatime component...
    pathlib.Path.mkdir(out_dir_path)
    #
    in_dir_file = askopenfilename(title='select the sessions list table...')
    in_dir_file = pathlib.Path(in_dir_file)

    # call the function to scan the system and finally returning a report log
    report_ = drive_scan(in_dir_path, in_dir_file, out_dir_path, now_)

    report_unq = report_[report_['uniqueExistence'] == True]  # choose only the ones with the unique existence
    if report_unq.empty:
        print(f'{TextColor.FAIL}NO unique sessions were found! check your inputs...{TextColor.ENDC}')
        usr_input = input('Do you want to start afresh? (Y/N)')
        if usr_input in ['yes', 'YES', 'y', 'Y']:
            break_loop = False
        elif usr_input in ['NO', 'no', 'N', 'n']:
            raise SystemExit('Exiting the program...')
    else:
        print(f'{TextColor.OKBLUE}"{len(report_unq)}" out of "{len(report_)}" were found as '
              f'unique sessions...{TextColor.ENDC}')
        usr_input = input('Do you want to continue(Y) or start afresh(N)?')
        if usr_input in ['yes', 'YES', 'y', 'Y']:
            break_loop = True
        elif usr_input in ['NO', 'no', 'N', 'n']:
            break_loop = False

conversion_report = pd.DataFrame()  # to write the conversion report
conversion_report['session'] = ''
conversion_report['session2csv'] = ''
conversion_report['csv2nwb'] = ''

# now iterate on all the existing sessions and per session call session2csv function
for cntr, index_ in enumerate(list(report_unq.index)):

    session_path = eval(report_unq.at[index_, 'parUnique'])[0]
    print(f'######\n'
          f'{TextColor.BOLD}({cntr+1}/{len(report_unq)}) evaluation of the following session path: \n'
          f'{session_path}{TextColor.ENDC}')
    #
    nwb_session_path_name = (f"{report_unq.at[index_, 'root']}_"
                             f"{report_unq.at[index_, 'Date']}_"
                             f"{report_unq.at[index_, 'Paradigm']}")
    conversion_report.at[cntr, 'session'] = nwb_session_path_name

    # try blocking for the session2csv
    try:
        to_feed = {
            'input_dir': session_path,
            'experimenter': report_unq.at[index_, 'Experimenter'],
            'convert_behavior': bool(report_unq.at[index_, 'Behaviour']),
            'convert_cardiac': bool(report_unq.at[index_, 'HeartRate']),
            'convert_thermal': bool(report_unq.at[index_, 'Thermal']),
            'description': 'na',  # temporary use for statesPaper | can be altered
            'doi': 'https://doi.org/10.1038/s41593-022-01252-w',  # temporary use for statesPaper | can be altered
            'keywords': 'Integrated cardio-behavioral defensive states'  # temporary use for statesPaper | can be altered
        }

        status_ = session2csv(**to_feed)
    except Exception as error:
        session2csv_error = error  # write the error to this variable, if any...
        conversion_report.at[cntr, 'session2csv'] = f'{type(error).__name__}: {error}'
        conversion_report.at[cntr, 'csv2nwb'] = 'na'
        print(f'{TextColor.FAIL}ERROR CAPTURED (session2csv): The session2csv ran into an error '
              f'-{type(error).__name__}: {error}- moving on to the next session...{TextColor.ENDC}')
        continue

    conversion_report.at[cntr, 'session2csv'] = status_  # session2csv status update
    path_to_csv = session_path / 'session2csv'  # in the case of any csv generation this folder would exist
    print(f'{TextColor.OKBLUE}** status of the session2csv(): "{status_}" **{TextColor.ENDC}')

    if status_ == 'conversionSuccessful':
        # try blocking to move on in huge batch conversions and capture the error risen from base_func_sheet
        try:
            # read in the main-info-sheet
            try:
                main_info_dict = pd.read_csv(path_to_csv / 'main-info-sheet.csv', index_col='data/meta').to_dict()
            except NameError:
                raise 'could not find main-info-sheet.csv... check your directories!'
            print(f'starting conversion of the session in the following directory to NWB... \n'
                  f'{session_path}')
            nwb_file = []  # to start with
            for key_ in main_info_dict.keys():
                pointer_ = main_info_dict[key_]
                for dum_ in list(pointer_.keys()):
                    # some time there is no mainData and only metaData, try blocking to account for this
                    try:
                        # to define absolute paths for each file (key)
                        pointer_.update({dum_: path_to_csv / pointer_[dum_]})
                    except:
                        pass  # pass if the value is nan
                exec(f'nwb_file = {key_}(nwb_file, pointer_)')
            # print('successfully converted...')

            # delete the generated csv files
            shutil.rmtree(path_to_csv)

            # make relevant directory
            nwb_session_path = out_dir_path / f'{nwb_session_path_name}_NWB'
            pathlib.Path.mkdir(nwb_session_path)

            # make directory for external files
            ext_file_path = nwb_session_path / 'recordings'
            pathlib.Path.mkdir(ext_file_path)

            # change the external path for the relevant path of the recordings
            rec_path = pathlib.Path(
                nwb_file.acquisition['behavior_recording'].external_file[0])  # as it is read as list
            shutil.copy2(rec_path, ext_file_path)
            nwb_file.acquisition['behavior_recording'].fields['external_file'] = (
                str(ext_file_path.relative_to(nwb_session_path) / rec_path.name))

            # write it onto the file
            with NWBHDF5IO(nwb_session_path / f'{nwb_session_path_name}_NWB-session.nwb', 'w') as io:
                io.write(nwb_file)
            print(f'{TextColor.OKGREEN}** NWB session conversion was successful! **{TextColor.ENDC}')
            conversion_report.at[cntr, 'csv2nwb'] = 'successful'
        except Exception as error:
            base_func_error = error  # write the error to this variable, if any...
            conversion_report.at[cntr, 'csv2nwb'] = f'{type(error).__name__}: {error}'
            print(f'{TextColor.FAIL}ERROR CAPTURED (base_func_sheet): The csv2nwb ran into an error '
                  f'-{type(error).__name__}: {error}- moving on to the next session...{TextColor.ENDC}')
            conversion_report.to_csv(out_dir_path / f'conversion_report_{now_}.csv')
            continue
    else:
        # delete the generated csv files, if any...
        try:
            shutil.rmtree(path_to_csv)
        except:
            pass
        #
        print(
            f'{TextColor.FAIL}WARNING CAPTURED (session2csv): Incomplete CSV conversion... '
            f'moving on to the next session...{TextColor.ENDC}')
        conversion_report.at[cntr, 'csv2nwb'] = 'na'
        conversion_report.to_csv(out_dir_path / f'conversion_report_{now_}.csv')
        continue

    conversion_report.to_csv(out_dir_path / f'conversion_report_{now_}.csv')

# TODO: return the list of remaining (unsuccessfully converted) sessions, if any at the end
