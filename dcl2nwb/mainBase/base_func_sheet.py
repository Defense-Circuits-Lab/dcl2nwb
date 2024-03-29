from pynwb import (
    NWBFile,
    TimeSeries,
    device,
)
from pynwb.behavior import (
    SpatialSeries,
    Position,
    BehavioralTimeSeries,
    BehavioralEpochs
)
from pynwb.file import Subject
from pynwb.misc import IntervalSeries
from pynwb.ogen import OptogeneticSeries
from pynwb.image import ImageSeries
from datetime import datetime
from dateutil import tz
import pandas as pd
import numpy as np
#
from ndx_ecg import (
    CardiacSeries,
    ECG,
    HeartRate,
    AuxiliaryAnalysis,
    ECGRecordingGroup,
    ECGRecDevice,
    ECGElectrodes,
    ECGChannels
)
from pathlib import WindowsPath


# create the nwb_file
def session_information(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    dict_ = pd.read_csv(file_to_read).to_dict()
    yr, mo, day = dict_['start_date'][0].split(', ')  # index 0 is for pandas convention
    hr, mnt, sec = dict_['start_time'][0].split(', ')
    start_time = datetime(int(yr), int(mo), int(day),
                          int(hr), int(mnt), int(sec),
                          tzinfo=tz.gettz(dict_['location'][0]))  # to be changed

    del dict_['start_date'], dict_['start_time'], dict_['location']  # not recognized by NWBFile
    # build a new dict to feed NWBFile
    dict_to_feed = {}
    # since no index is set to DataFrame read onto the system, exclude the 0th element from keys()
    [dict_to_feed.update({key_: dict_[key_][0]}) for key_ in list(dict_.keys())[1:]]
    dict_to_feed.update({'session_start_time': start_time})
    dict_to_feed.update({'keywords': dict_to_feed['keywords'].split(', ')})  # needs a list not a str type
    nwb_file = NWBFile(
        **dict_to_feed
    )

    return nwb_file


def subject_information(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    dict_ = pd.read_csv(file_to_read).to_dict()
    # build a new dict to feed
    dict_to_feed = {}
    # since no index is set to DataFrame read onto the system, exclude the 0th element from keys()
    [dict_to_feed.update({key_: dict_[key_][0]}) for key_ in list(dict_.keys())[1:]]

    # defining the subject
    nwb_file.subject = Subject(
        **dict_to_feed
    )

    return nwb_file


def devices_information(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    df_ = pd.read_csv(file_to_read)

    for dum_ in list(df_.index.values):
        # build a new dict to feed
        dict_to_feed = {}
        # since no index is set to DataFrame read onto the system, exclude the 0th element from keys()
        [dict_to_feed.update({key_: df_.loc[dum_][key_]}) for key_ in list(df_.keys()[1:])]
        device_obj = device.Device(
            **dict_to_feed
        )
        nwb_file.add_device(device_obj)

    return nwb_file


def images_information(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    df_ = pd.read_csv(file_to_read)

    for dum_ in list(df_.index.values):
        # build a new dict to feed
        dict_to_feed = {}
        # since no index is set to DataFrame read onto the system, exclude the 0th element from keys()
        [dict_to_feed.update({key_: df_.loc[dum_][key_]}) for key_ in list(df_.keys()[1:])]
        dict_to_feed.update({'format': 'external'})  # external format setting
        dict_to_feed.update({'external_file': [dict_to_feed['external_file']]})  # external format setting
        dict_to_feed.update({'device': nwb_file.get_device(dict_to_feed['device'])})  # external format setting
        images_obj = ImageSeries(
            **dict_to_feed
        )
        nwb_file.add_acquisition(images_obj)

    return nwb_file


def ecg_device(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    df_ = pd.read_csv(file_to_read)

    for dum_ in list(df_.index.values):
        dum_dev_pointer = nwb_file.get_device(df_.loc[dum_]['endpoint_recording_device'])  # get the main device
        # build a new dict to feed
        dict_to_feed = {}
        # since no index is set to DataFrame read onto the system, exclude the 0th element from keys()
        [dict_to_feed.update({key_: df_.loc[dum_][key_]}) for key_ in list(df_.keys()[1:])]
        # extra update
        dict_to_feed.update({'name': 'recording_device'})  # default name for future reference
        dict_to_feed.update({'endpoint_recording_device': dum_dev_pointer})

        device_obj = ECGRecDevice(
            **dict_to_feed
        )
        nwb_file.add_device(device_obj)

    return nwb_file


def acquisition(nwb_file, file_pointer):

    file_to_read_meta = file_pointer['metaData']  # name of file to read
    # if not file_to_read_meta.split('.')[-1] == 'csv':
    #     file_to_read_meta += '.csv'
    df_meta = pd.read_csv(file_to_read_meta, index_col=0)  # set data_name as index
    content_name_list = list(df_meta.index)  # listing the names of data content

    file_to_read_main = file_pointer['mainData']  # name of file to read
    # if not file_to_read_main.split('.')[-1] == 'csv':
    #     file_to_read_main += '.csv'
    df_main = pd.read_csv(file_to_read_main)

    for dum_ in content_name_list:
        # build a new dict to feed
        dict_to_feed = {}
        [dict_to_feed.update({key_: df_meta.loc[dum_][key_]}) for key_ in list(df_meta.keys())]
        time_array = df_main[f'{dum_}_time'].to_numpy()
        data_array = df_main[f'{dum_}_data'].to_numpy()
        # logical exclusion of nan for array size difference
        dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                             'data': data_array[~np.isnan(data_array)]})
        acquisition_obj = TimeSeries(
            **dict_to_feed
        )
        nwb_file.add_acquisition(acquisition_obj)

    return nwb_file


def processed_data(nwb_file, file_pointer):

    file_to_read_meta = file_pointer['metaData']  # name of file to read
    # if not file_to_read_meta.split('.')[-1] == 'csv':
    #     file_to_read_meta += '.csv'
    df_meta = pd.read_csv(file_to_read_meta, index_col=0)  # set data_name as index
    content_name_list = list(df_meta.index)  # listing the names of data content

    file_to_read_main = file_pointer['mainData']  # name of file to read
    # if not file_to_read_main.split('.')[-1] == 'csv':
    #     file_to_read_main += '.csv'
    df_main = pd.read_csv(file_to_read_main)

    # create modules
    data_module_dict = {}
    [data_module_dict.update({ind_: df_meta.loc[ind_]['module_name']}) for ind_ in content_name_list]
    modules_nam = list(set(list(df_meta.module_name)))  # list of modules names in the processed data
    modules_des = list(set(list(df_meta.module_description)))  # list of modules descriptions in the processed data
    for dum_ in range(len(modules_nam)):
        exec(
            f'{modules_nam[dum_]}_module = nwb_file.create_processing_module('
            f'name=\'{modules_nam[dum_]}\','
            f'description=\'{modules_des[dum_]}\''
            f')'
        )

    for dum_ in content_name_list:
        # exclude ['module_name', 'module_description'] from metadata feed to TimeSeries
        keys_to_exclude = ['module_name', 'module_description']
        # print(keys_to_exclude)
        # build a new dict to feed
        dict_to_feed = {}
        [dict_to_feed.update({key_: df_meta.loc[dum_][key_]}) for key_ in list(df_meta.keys())
         if key_ not in keys_to_exclude]
        time_array = df_main[f'{dum_}_time'].to_numpy()
        data_array = df_main[f'{dum_}_data'].to_numpy()
        # logical exclusion of nan for array size difference
        dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                             'data': data_array[~np.isnan(data_array)]})
        processed_data_obj = TimeSeries(
            **dict_to_feed
        )
        eval(f'{data_module_dict[dum_]}_module').add(processed_data_obj)  # add processed data to it's module

    return nwb_file


def behavioral_data(nwb_file, file_pointer):

    file_to_read_meta = file_pointer['metaData']  # name of file to read
    # if not file_to_read_meta.split('.')[-1] == 'csv':
    #     file_to_read_meta += '.csv'
    df_meta = pd.read_csv(file_to_read_meta, index_col=0)  # set data_name as index
    content_name_list = list(df_meta.index)  # listing the names of data content

    file_to_read_main = file_pointer['mainData']  # name of file to read
    # if not file_to_read_main.split('.')[-1] == 'csv':
    #     file_to_read_main += '.csv'
    df_main = pd.read_csv(file_to_read_main)

    # create module/object to start integration
    behavior_module = nwb_file.create_processing_module(
        name='behavior',
        description='processed behavioral data'
    )
    position_obj = Position(
        name='Position'
    )
    behavioral_time_series_obj = BehavioralTimeSeries(
        name='BehavioralTimeSeries'
    )
    behavioral_epochs_obj = BehavioralEpochs(
        name='BehavioralEpochs'
    )

    for dum_ in content_name_list:
        # exclude nans from metadata
        keys_to_exclude = ['interface_subtype']
        [keys_to_exclude.append(key_) for key_ in list(df_meta.keys()) if pd.isnull(df_meta.loc[dum_][key_])]
        # print(keys_to_exclude)
        # build a new dict to feed
        dict_to_feed = {}
        [dict_to_feed.update({key_: df_meta.loc[dum_][key_]}) for key_ in list(df_meta.keys())
         if key_ not in keys_to_exclude]

        if df_meta.loc[dum_]['interface_subtype'] == 'position':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})
            spatial_series_obj = SpatialSeries(
                **dict_to_feed
            )
            position_obj.add_spatial_series(spatial_series_obj)

        elif df_meta.loc[dum_]['interface_subtype'] == 'time_series':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})
            time_series_obj = TimeSeries(
                **dict_to_feed
            )
            behavioral_time_series_obj.add_timeseries(time_series_obj)

        elif df_meta.loc[dum_]['interface_subtype'] == 'epochs':

            time_array = df_main[f'{dum_}_time']

            if not isinstance(time_array[0], str):
                time_array = time_array.to_numpy()
                data_array = df_main[f'{dum_}_data'].to_numpy()
                time_stamps = time_array[~np.isnan(data_array)]
                data_ = data_array[~np.isnan(data_array)]
                # preconditioning data
                indexing_ = np.diff(data_)  # epoch starting and ending points with 1 and -1 respectively
                transition_points = np.where(np.abs(indexing_) == 1)[0]  # [0] to avoid tuples
                # the line below would return int dtype to get rid of a nwb warning
                transition_labeling = indexing_[transition_points].astype('int')  # start(1) or end(-1) | qualitatively
                """note:
                assumption: if a behavior is observed at each frame then: '1', else: '0', so frame specific identification  
                the start time is exactly the first frame with 1;
                the end time stamp of an epoch is the first 0 frame after the last 1,
                this is the reason we move the arguments of the next line 1 step forward
                the above line is qualitative so the indexing would make no problem in general
                """
                transition_time_stamps = time_stamps[transition_points + 1]  # start(1) or end(-1) time stamps of an epoch
                # check whether the session already started with an epoch
                if np.any(transition_points) and indexing_[transition_points[0]] == -1:
                    transition_labeling = \
                        np.append(1, transition_labeling)
                    transition_time_stamps =\
                        np.append(time_stamps[0], transition_time_stamps)
                #
                dict_to_feed.update({'timestamps': transition_time_stamps,
                                     'data': transition_labeling})

            elif isinstance(eval(time_array[0]), list):
                transition_time_stamps = []
                [transition_time_stamps.extend([float(eval(stamp_)[0]), float(eval(stamp_)[1])])
                 for stamp_ in time_array if not pd.isnull(stamp_)]  # creating stamps from given ranges
                transition_labeling = []
                [transition_labeling.extend([1, -1]) for stamp_ in time_array
                 if not pd.isnull(stamp_)]
                #
                dict_to_feed.update({'timestamps': transition_time_stamps,
                                     'data': transition_labeling})

            interval_series_obj = IntervalSeries(
                **dict_to_feed
            )
            behavioral_epochs_obj.add_interval_series(interval_series_obj)

    behavior_module.add(position_obj)  # add position_obj to behavior module
    behavior_module.add(behavioral_time_series_obj)  # add time_series_obj to behavior module
    behavior_module.add(behavioral_epochs_obj)  # add behavioral_epochs_obj to behavior module

    return nwb_file


def stimulation_data(nwb_file, file_pointer):

    file_to_read_meta = file_pointer['metaData']  # name of file to read
    # if not file_to_read_meta.split('.')[-1] == 'csv':
    #     file_to_read_meta += '.csv'
    df_meta = pd.read_csv(file_to_read_meta, index_col=0)  # set data_name as index
    content_name_list = list(df_meta.index)  # listing the names of data content

    file_to_read_main = file_pointer['mainData']  # name of file to read
    # if not file_to_read_main.split('.')[-1] == 'csv':
    #     file_to_read_main += '.csv'
    df_main = pd.read_csv(file_to_read_main)

    for dum_ in content_name_list:
        # exclude nans from metadata
        keys_to_exclude = ['stim_type']
        [keys_to_exclude.append(key_) for key_ in list(df_meta.keys()) if pd.isnull(df_meta.loc[dum_][key_])]
        # print(keys_to_exclude)
        # build a new dict to feed
        dict_to_feed = {}
        [dict_to_feed.update({key_: df_meta.loc[dum_][key_]}) for key_ in list(df_meta.keys())
         if key_ not in keys_to_exclude]

        if df_meta.loc[dum_]['stim_type'] == 'context':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})

            time_series_obj = TimeSeries(
                **dict_to_feed
            )

            nwb_file.add_stimulus(time_series_obj)

        elif df_meta.loc[dum_]['stim_type'] == 'ogen':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})
            device_obj = nwb_file.get_device(
                name=dict_to_feed['device']
            )
            ogen_site_obj = nwb_file.create_ogen_site(
                name=dict_to_feed['name'],
                device=device_obj,
                description=dict_to_feed['description'],
                excitation_lambda=float(dict_to_feed['excitation_lambda']),  # nm
                location=dict_to_feed['location']
            )
            ogen_series_obj = OptogeneticSeries(
                name=dict_to_feed['name'],
                timestamps=dict_to_feed['timestamps'],
                data=dict_to_feed['data'],
                site=ogen_site_obj,
                comments=dict_to_feed['comments']
            )
            nwb_file.add_stimulus(ogen_series_obj)

    return nwb_file


def ecg_electrodes(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    df_ = pd.read_csv(file_to_read)
    ecg_electrodes_table = ECGElectrodes(
        description='ECG recording electrodes table'
    )

    # add electrodes
    for ind_ in list(df_.index):
        ecg_electrodes_table.add_row(
            electrode_name=df_.at[ind_, 'electrode_name'],
            electrode_location=df_.at[ind_, 'electrode_location'],
            electrode_info=df_.at[ind_, 'electrode_info']
        )

    # adding the object of DynamicTable
    nwb_file.add_acquisition(ecg_electrodes_table)  # storage point for DT

    return nwb_file


def ecg_channels(nwb_file, file_pointer):

    file_to_read = file_pointer['metaData']  # name of file to read
    # if not file_to_read.split('.')[-1] == 'csv':
    #     file_to_read += '.csv'
    df_ = pd.read_csv(file_to_read)
    ecg_channels_table = ECGChannels(
        description='ECG recording electrodes table'
    )

    # add electrodes
    for ind_ in list(df_.index):
        ecg_channels_table.add_row(
            channel_name=df_.at[ind_, 'channel_name'],
            channel_type=df_.at[ind_, 'channel_type'],
            involved_electrodes=df_.at[ind_, 'involved_electrodes'],
            channel_info=df_.at[ind_, 'channel_info']
        )

    # adding the object of DynamicTable
    nwb_file.add_acquisition(ecg_channels_table)  # storage point for DT

    return nwb_file


def cardiac_data(nwb_file, file_pointer):

    file_to_read_meta = file_pointer['metaData']  # name of file to read
    # if not file_to_read_meta.split('.')[-1] == 'csv':
    #     file_to_read_meta += '.csv'
    df_meta = pd.read_csv(file_to_read_meta, index_col=0)  # set data_name as index
    content_name_list = list(df_meta.index)  # listing the names of data content

    file_to_read_main = file_pointer['mainData']  # name of file to read
    # if not file_to_read_main.split('.')[-1] == 'csv':
    #     file_to_read_main += '.csv'
    df_main = pd.read_csv(file_to_read_main)

    # create module/object to start integration
    cardio_module = nwb_file.create_processing_module(
        name='cardio_module',
        description='module to store processed cardiac data'
    )

    # need to define the channels_group first
    ecg_recording_group  = ECGRecordingGroup(
        name='recording_group',
        group_description='a group to store electrodes and channels table',
        electrodes=nwb_file.get_acquisition('electrodes'),
        channels=nwb_file.get_acquisition('channels'),
        recording_device=nwb_file.get_device('recording_device')
    )
    nwb_file.add_lab_meta_data(ecg_recording_group)  # storage point for custom LMD

    for dum_ in content_name_list:
        # exclude nans from metadata
        keys_to_exclude = ['processing_description', 'interface_subtype', 'interface_name', 'type']
        # extend the exclusions
        [keys_to_exclude.append(key_) for key_ in list(df_meta.keys()) if pd.isnull(df_meta.loc[dum_][key_])]
        # print(keys_to_exclude)
        # build a new dict to feed
        dict_to_feed = {}
        [dict_to_feed.update({key_: df_meta.loc[dum_][key_]}) for key_ in list(df_meta.keys())
         if key_ not in keys_to_exclude]

        if df_meta.loc[dum_]['interface_subtype'] == 'ECG':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})
            # extra update
            dict_to_feed.update({'recording_group': ecg_recording_group})
            #
            cardiac_series_obj = CardiacSeries(
                **dict_to_feed
            )
            # go with default name
            if pd.isnull(df_meta.loc[dum_]['interface_name']):
                ecg_object = ECG(
                    cardiac_series=[cardiac_series_obj],
                    processing_description=df_meta.loc[dum_]['processing_description']
                )
            # also give it a name: should be used for more than one instance of each interface
            else:
                ecg_object = ECG(
                    name=df_meta.loc[dum_]['interface_name'],
                    cardiac_series=[cardiac_series_obj],
                    processing_description=df_meta.loc[dum_]['processing_description']
                )
            # now writing:
            if df_meta.loc[dum_]['type'] == 'R':
                # adding the raw acquisition of ECG to the nwb_file inside an 'ECG' container
                nwb_file.add_acquisition(ecg_object)
            elif df_meta.loc[dum_]['type'] == 'P':
                # adding the processed ECG to the nwb_file inside an 'ECG' container, to cardio_module
                cardio_module.add(ecg_object)

        elif df_meta.loc[dum_]['interface_subtype'] == 'HR':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})
            # extra update
            dict_to_feed.update({'recording_group': ecg_recording_group})
            #
            cardiac_series_obj = CardiacSeries(
                **dict_to_feed
            )
            # go with default name
            if pd.isnull(df_meta.loc[dum_]['interface_name']):
                hr_object = HeartRate(
                    cardiac_series=[cardiac_series_obj],
                    processing_description=df_meta.loc[dum_]['processing_description']
                )
            # also give it a name: should be used for more than one instance of each interface
            else:
                hr_object = HeartRate(
                    name=df_meta.loc[dum_]['interface_name'],
                    cardiac_series=[cardiac_series_obj],
                    processing_description=df_meta.loc[dum_]['processing_description']
                )
            # adding the processed ECG to the nwb_file inside an 'ECG' container, to cardio_module
            cardio_module.add(hr_object)

        elif df_meta.loc[dum_]['interface_subtype'] == 'AUX':

            time_array = df_main[f'{dum_}_time'].to_numpy()
            data_array = df_main[f'{dum_}_data'].to_numpy()
            # logical exclusion of nan for array size difference
            dict_to_feed.update({'timestamps': time_array[~np.isnan(data_array)],
                                 'data': data_array[~np.isnan(data_array)]})
            # extra update
            dict_to_feed.update({'recording_group': ecg_recording_group})
            #
            cardiac_series_obj = CardiacSeries(
                **dict_to_feed
            )
            # go with default name
            if pd.isnull(df_meta.loc[dum_]['interface_name']):
                aux_object = AuxiliaryAnalysis(
                    cardiac_series=[cardiac_series_obj],
                    processing_description=df_meta.loc[dum_]['processing_description']
                )
            # also give it a name: should be used for more than one instance of each interface
            else:
                aux_object = AuxiliaryAnalysis(
                    name=df_meta.loc[dum_]['interface_name'],
                    cardiac_series=[cardiac_series_obj],
                    processing_description=df_meta.loc[dum_]['processing_description']
                )
            # adding the processed ECG to the nwb_file inside an 'ECG' container, to cardio_module
            cardio_module.add(aux_object)

    return nwb_file
