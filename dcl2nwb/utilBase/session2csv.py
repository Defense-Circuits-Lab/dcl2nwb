"""A module for converting each session into corresponding pre-structured CSV tables.
Evoked at each session from the main conversion module, the products would be finally
removed from within the main module itself.
"""

import numpy as np
import pandas as pd
from scipy.io import loadmat
import pathlib
import warnings
import shutil


def session2csv(input_dir, experimenter,
                convert_behavior, convert_cardiac, convert_thermal,
                description='na',
                doi='https://doi.org/10.1038/s41593-022-01252-w',
                keywords='Integrated cardio-behavioral defensive states'):
    """
    A function to convert sessions into pre-structured csv files to be fed into dcl2nwb pipeline.
    :param input_dir: the path object pointing to a single session
    :param experimenter: the name of the experimenter of the session
    :param convert_behavior: a boolean indicator of whether to convert the behavior data in the session
    :param convert_cardiac: a boolean indicator of whether to convert the cardiac data in the session
    :param convert_thermal: a boolean indicator of whether to convert the thermal data in the session
    :param description: a global description of the project (default: 'na')
    :param doi: doi of the relevant research work (default: 'na')
    :param keywords: keywords of the research data (default: 'na')
    :return: if successful: 'conversionSuccessful', i.e., a folder containing all the converted csv files is generated,
             otherwise: on each level can return different reports of failure as strings
    """

    mainInfoSheet = {'data/meta': ['mainData', 'metaData']}  # to be updated

    out_dir = input_dir / 'session2csv'  # temporary output folder
    if out_dir.exists():
        shutil.rmtree(out_dir)  # if already exists removes it; I want it afresh!
        pathlib.Path.mkdir(out_dir)
    else:
        pathlib.Path.mkdir(out_dir)

    lines_main_path = r'F:\Jeremy\MATLAB_Scripts\Toolbox\+DataBase\+Lists\MouseLines_List.mat'  # to be fixed at the DCL
    # lines_main_path = r'C:\Users\DCL\Desktop\DCL-files\MouseLines_List.mat'  # test on my PC
    try:
        lines_main = loadmat(lines_main_path)  # to be fixed at the DCL
    except:
        warnings.warn('The following path is not found... IGNORING...\n'
                      f'{lines_main_path}')
        return 'noLinesManual'

    behavior_list = [
        'Rearing', 'rearing', 'Immobility', 'immobility', 'Remaining', 'remaining',
        'locomotion', 'Locomotion', 'AreaBound', 'area_bound', 'Area-bound',
        'StretchAttend', 'stretch_attend', 'Stretch-attend posture',
        'Grooming', 'grooming', 'TailRattling', 'tail_rattling', 'Tail rattling']

    # get a *.pl2 file from the path and split the name '_' to get Line, MouseID, date, paradigm
    pl2_list = list(input_dir.glob('*.pl2'))  # checking if the pl2 files exist
    if any(pl2_list) and not len(pl2_list) > 1:
        base_split = pl2_list[0].stem.split('_')  # split the parts of the base name
        line = base_split[0]
        mouse_id = base_split[1]
        date = base_split[2]
        paradigm = base_split[3]
    else:
        warnings.warn('Either NO or MULTIPLE <.pl2> files found in the following path... IGNORING...\n'
                      f'{input_dir}')
        return 'noProperSession'

    # make the structured table of meta-data here using the things uploaded before
    dict_session = {
        'session_description': paradigm,
        'identifier': f'{line}_{mouse_id}:{paradigm}',
        'start_date': f'20{date[:2]}, {date[2:4]}, {date[4:]}',
        'start_time': '00, 00, 00',  # defaults to the 00:00:00, since no information on time is provided
        'location': 'Europe/Berlin',
        'session_id': pl2_list[0].stem,
        'experimenter': experimenter,
        'lab': 'Defense Circuits Lab',  # default in dcl2nwb
        'institution': 'Institute of Clinical Neurobiologie - UKW',  # default in dcl2nwb
        'experiment_description': description,
        'related_publications': doi,
        'keywords': keywords
    }
    # export the session-meta
    df_ = pd.DataFrame(dict_session, index=[0])  # to save all scalars | pandas
    df_.to_csv(out_dir / 'session-meta.csv')
    # adding to the main-info-sheet
    mainInfoSheet.update({
        'session_information': ['', 'session-meta.csv']
    })

    #
    # mouse meta from file (if existing)
    #

    lines_list = [lines_main['Lines'][i][0][0] for i in range(len(lines_main['Lines']))]  # list of all main lines
    try:
        full_line = lines_main['Lines'][lines_list.index(line)][1][0]  # subject species fullname from the main file
        if full_line == 'Bl6':
            full_line = 'Bl6/C57'
        else:
            full_line = f'Bl6/C57-{full_line}'
    except:
        warnings.warn(
            'The following line (from the following path) does not exist in the main list of the lines... IGNORING...\n'
            f'{line} from\n'
            f'{input_dir}')
        return 'noMatchingLine'

    meta_file = list(input_dir.parent.glob(f'{line}_{mouse_id}_Meta.mat'))  # must be located in the root folder
    if any(meta_file):
        meta_file = loadmat(meta_file[0])
        subject_genotype = meta_file['General'][1][6][0]
        subject_sex = meta_file['General'][1][4][0]
        # subject_dob = meta_file['General'][1][5][0]  # could be added as a date-time format later
    else:
        subject_genotype = 'na'
        subject_sex = 'na'
        # subject_dob = 'na'  # could be added as a date-time format later

    dict_subject = {
        'description': 'na',
        'species': f'{full_line}',
        'genotype': f'{subject_genotype}',
        'sex': f'{subject_sex}',
        # 'date_of_birth': f'{subject_dob}',  # could be added as a date-time format later
    }
    # export the subject-meta
    df_ = pd.DataFrame(dict_subject, index=[0])  # to save all scalars | pandas
    df_.to_csv(out_dir / 'subject-meta.csv')
    # adding to the main-info-sheet
    mainInfoSheet.update({
        'subject_information': ['', 'subject-meta.csv']
    })

    # devices meta
    dict_devices = {
        'name': ['endpoint_recording_device', 'Pike camera', 'A655sc', 'RZ6', 'Ce:YAG Laser diode', 'Stimulus isolator'],
        'manufacturer': ['Plexon(Omniplex)', 'Allied vision', 'FLIR', 'Tucker-Davis systems', 'Doric', 'npi'],
        'description': ['Main digital-analog recording system',
                        'Top view RGB camera',
                        'Top view for infra-red camera',
                        'Real-time processor; sound generation',
                        'Light source for opto-genetic stimulations',
                        'DC current generator to deliver foot shocks']
    }
    df_ = pd.DataFrame(dict_devices)
    df_.to_csv(out_dir / 'devices-meta.csv')
    # adding to the main-info-sheet
    mainInfoSheet.update({
        'devices_information': ['', 'devices-meta.csv']
    })

    #
    # behavioral data
    #

    if convert_behavior:
        dict_behavior = {}  # to be updated later
        dict_behavior_meta = {
            'data_index': [],
            'name': [],
            'description': [],
            'reference_frame': [],
            'unit': [],
            'comments': [],
            'interface_subtype': []
        }
        dvt_file = list(input_dir.glob('*.DVT'))
        if any(dvt_file):
            file_ = pd.read_csv(dvt_file[0], header=None)
            avi_times = file_.iloc[:, 1].to_numpy()  # video times array
        else:
            warnings.warn(
                'Could NOT find a <.DVT> from the following path) does not exist in the main list of the lines... '
                'IGNORING...\n'
                f'{line} from\n'
                f'{input_dir}')
            return 'noDVT'
        tracking_file = list(input_dir.glob('*_Tracking.mat'))
        if any(tracking_file):
            file_ = loadmat(tracking_file[0])
            x_pos = file_['RGB']['Center'][0][0][:, 0]
            dict_behavior.update({'x_coordinates_time': avi_times,
                                  'x_coordinates_data': x_pos})
            dict_behavior_meta['data_index'].append('x_coordinates')
            dict_behavior_meta['name'].append('x_coordinates')
            dict_behavior_meta['description'].append('mouse x position')
            dict_behavior_meta['reference_frame'].append('na')
            dict_behavior_meta['unit'].append('px')
            dict_behavior_meta['comments'].append('none')
            dict_behavior_meta['interface_subtype'].append('position')
            #
            y_pos = file_['RGB']['Center'][0][0][:, 1]
            dict_behavior.update({'y_coordinates_time': avi_times,
                                  'y_coordinates_data': y_pos})
            dict_behavior_meta['data_index'].append('y_coordinates')
            dict_behavior_meta['name'].append('y_coordinates')
            dict_behavior_meta['description'].append('mouse y position')
            dict_behavior_meta['reference_frame'].append('na')
            dict_behavior_meta['unit'].append('px')
            dict_behavior_meta['comments'].append('none')
            dict_behavior_meta['interface_subtype'].append('position')
            #
            motion_measure = file_['RGB']['MotionMeasure'][0][0][:, 0]
            dict_behavior.update({'motion_measure_time': avi_times,
                                  'motion_measure_data': motion_measure})
            dict_behavior_meta['data_index'].append('motion_measure')
            dict_behavior_meta['name'].append('motion_measure')
            dict_behavior_meta['description'].append('motion measure')
            dict_behavior_meta['reference_frame'].append(np.nan)  # has to be nan to be excluded in base_func_sheet
            dict_behavior_meta['unit'].append('au')
            dict_behavior_meta['comments'].append('none')
            dict_behavior_meta['interface_subtype'].append('time_series')
        else:
            warnings.warn(
                'Could NOT find the <_Tracking.mat> from the following path... IGNORING...\n'
                f'{input_dir}')
            return 'noTrackingFile'

        # speed data and epochs:
        tempBehavior_file = list(input_dir.glob('*_TempBehaviour.mat'))
        if any(tempBehavior_file):
            file_ = loadmat(tempBehavior_file[0])
            speed_data = file_['StepSpeed']
            speed_data = speed_data.reshape(len(speed_data), )  # to make an acceptable shape
            dict_behavior.update({'speed_time': avi_times,
                                  'speed_data': speed_data})
            dict_behavior_meta['data_index'].append('speed')
            dict_behavior_meta['name'].append('speed')
            dict_behavior_meta['description'].append('step speed of the mouse')
            dict_behavior_meta['reference_frame'].append(np.nan)  # has to be nan to be excluded in base_func_sheet
            dict_behavior_meta['unit'].append('m.s-1')
            dict_behavior_meta['comments'].append('none')
            dict_behavior_meta['interface_subtype'].append('time_series')
            # epochs:
            for beh_ in behavior_list:
                # see if exists
                try:
                    epoch_range = file_['Data'][beh_][0][0]
                except:
                    continue
                #
                range_list = [f'[{epoch_range[i, 0]}, {epoch_range[i, 1]}]' for i in range(len(epoch_range))]
                dict_behavior.update(
                    {f'{beh_}_time': range_list,  # range_list may need to be converted into an np.array
                     f'{beh_}_data': [np.nan for i in range(len(range_list))]})
                dict_behavior_meta['data_index'].append(f'{beh_}')
                dict_behavior_meta['name'].append(f'{beh_}')
                dict_behavior_meta['description'].append(f'epoch range for the behavior {beh_}')
                dict_behavior_meta['reference_frame'].append(np.nan)
                dict_behavior_meta['unit'].append('nan')
                dict_behavior_meta['comments'].append('none')
                dict_behavior_meta['interface_subtype'].append('epochs')
        else:
            warnings.warn(
                'Could NOT find the <_TempBehaviour.mat> from the following path... IGNORING...\n'
                f'{input_dir}')
            return 'noTempBehaviourFile'

        # export the dict_behaviour
        df_ = pd.DataFrame.from_dict(dict_behavior, orient='index').transpose()
        df_.set_index(list(dict_behavior.keys())[0],
                      inplace=True)  # just to get rid of indexing columns in the out.csv file
        df_.to_csv(out_dir / 'behavioralData.csv')

        # export the dict_behaviour_meta
        df_ = pd.DataFrame(dict_behavior_meta)
        df_.set_index('data_index', inplace=True)
        df_.to_csv(out_dir / 'behavioralData-meta.csv')

        # adding to the main-info-sheet
        mainInfoSheet.update({
            'behavioral_data': ['behavioralData.csv', 'behavioralData-meta.csv']
        })

    #
    # cardiac data
    #

    if convert_cardiac:

        # ECG device meta
        dict_ecg_dev = {
            'manufacturer': ['npi'],
            'description': ['Modular amplifier for electro-physiological recordings'],
            'filtering': ['30-1000Hz bandpass'],
            'gain': ['tuned to 1000'],
            'offset': ['set to 0'],
            'synchronization': ['intrinsically taken care of via the Plexon system (endpoint-recording-device)'],
            'endpoint_recording_device': ['endpoint_recording_device']
        }
        df_ = pd.DataFrame(dict_ecg_dev)
        df_.to_csv(out_dir / 'ecg-device-meta.csv')
        # adding to the main-info-sheet
        mainInfoSheet.update({
            'ecg_device': ['', 'ecg-device-meta.csv']
        })

        # ECG electrodes meta
        dict_ = {
            'electrode_name': ['el_0', 'el_1', 'ref'],
            'electrode_location': ['right upper-chest', 'left lower-chest', 'top of the head'],
            'electrode_info': ['none', 'none', 'none']
        }
        df_ = pd.DataFrame(dict_)
        df_.to_csv(out_dir / 'ecg-electrodes-meta.csv')
        # adding to the main-info-sheet
        mainInfoSheet.update({
            'ecg_electrodes': ['', 'ecg-electrodes-meta.csv']
        })

        # ECG channels meta
        dict_ = {
            'channel_name': ['ch_0', 'ch_1'],
            'channel_type': ['single', 'differential'],
            'involved_electrodes': ['el_1', 'el_0 and el_1'],
            'channel_info': ['none', 'none']
        }
        df_ = pd.DataFrame(dict_)
        df_.to_csv(out_dir / 'ecg-channels-meta.csv')
        # adding to the main-info-sheet
        mainInfoSheet.update({
            'ecg_channels': ['', 'ecg-channels-meta.csv']
        })

        dict_cardiac = {}  # to be updated later
        dict_cardiac_meta = {
            'data_index': [],
            'name': [],
            'unit': [],
            'processing_description': [],
            'interface_subtype': [],
            'interface_name': [],
            'type': []
        }

        cardiac_file = list(input_dir.glob('complementary_exports/*_CardiacData.mat'))
        if any(cardiac_file):
            file_ = loadmat(cardiac_file[0])

            ecg_time = file_['cardiacData']['ecg_time'][0][0]
            ecg_time = ecg_time.reshape(len(ecg_time), )  # to make an acceptable shape
            ecg_data = file_['cardiacData']['ecg_data'][0][0]
            ecg_data = ecg_data.reshape(len(ecg_data), )  # to make an acceptable shape
            #
            dict_cardiac.update({'ecg_time': ecg_time,
                                 'ecg_data': ecg_data})
            dict_cardiac_meta['data_index'].append('ecg')
            dict_cardiac_meta['name'].append('ECG')
            dict_cardiac_meta['unit'].append('mV')
            dict_cardiac_meta['processing_description'].append('Raw ECG recording')
            dict_cardiac_meta['interface_subtype'].append('ECG')
            dict_cardiac_meta['interface_name'].append('nan')
            dict_cardiac_meta['type'].append('R')
            ##
            hr_time = file_['cardiacData']['heartRate_time'][0][0]
            hr_time = hr_time.reshape(len(hr_time), )  # to make an acceptable shape
            hr_data = file_['cardiacData']['heartRate_data'][0][0]
            hr_data = hr_data.reshape(len(hr_data), )  # to make an acceptable shape
            #
            dict_cardiac.update({'heartRate_time': hr_time,
                                 'heartRate_data': hr_data})
            dict_cardiac_meta['data_index'].append('heartRate')
            dict_cardiac_meta['name'].append('Heart Rate')
            dict_cardiac_meta['unit'].append('bpm')
            dict_cardiac_meta['processing_description'].append('Heart Rate')
            dict_cardiac_meta['interface_subtype'].append('HR')
            dict_cardiac_meta['interface_name'].append('nan')
            dict_cardiac_meta['type'].append('nan')
        else:
            warnings.warn(
                'Could NOT find the -CardiacData export from ECGLog- from the following path... IGNORING...\n'
                f'{input_dir / "complementary_exports"}')
            return 'noCardiacDataExport'

        # secondary readouts
        procHR_file = list(input_dir.glob('*_ProcHR.mat'))
        if any(procHR_file):
            file_ = loadmat(procHR_file[0])

            time_stamp = file_['Times']
            time_stamp = time_stamp.reshape(len(time_stamp), )  # to make an acceptable shape

            ceil_data = file_['Loess']
            ceil_data = ceil_data.reshape(len(ceil_data), )  # to make an acceptable shape
            #
            dict_cardiac.update({'ceiling_time': time_stamp,
                                 'ceiling_data': ceil_data})
            dict_cardiac_meta['data_index'].append('ceiling')
            dict_cardiac_meta['name'].append('ceiling data')
            dict_cardiac_meta['unit'].append('bpm')
            dict_cardiac_meta['processing_description'].append('ceiling data')
            dict_cardiac_meta['interface_subtype'].append('AUX')
            dict_cardiac_meta['interface_name'].append('ceiling')
            dict_cardiac_meta['type'].append('nan')
            #
            hr2ceil_data = file_['HRtoCeil']
            hr2ceil_data = hr2ceil_data.reshape(len(hr2ceil_data), )  # to make an acceptable shape
            #
            dict_cardiac.update({'hr2ceil_time': time_stamp,
                                 'hr2ceil_data': hr2ceil_data})
            dict_cardiac_meta['data_index'].append('hr2ceil')
            dict_cardiac_meta['name'].append('heart rate to ceiling')
            dict_cardiac_meta['unit'].append('bpm')
            dict_cardiac_meta['processing_description'].append('heart rate to ceiling')
            dict_cardiac_meta['interface_subtype'].append('HR')
            dict_cardiac_meta['interface_name'].append('hr2ceil')
            dict_cardiac_meta['type'].append('nan')
            #
            Wv_time_stamp = file_['HeartRateWv']['Times'][0][0].transpose()
            Wv_time_stamp = Wv_time_stamp.reshape(len(Wv_time_stamp), )  # to make an acceptable shape

            lf_data = file_['HeartRateWv']['High'][0][0][0][0]['Signal'].transpose()
            lf_data = lf_data.reshape(len(lf_data), )  # to make an acceptable shape
            #
            dict_cardiac.update({'lf_time': Wv_time_stamp,
                                 'lf_data': lf_data})
            dict_cardiac_meta['data_index'].append('lf')
            dict_cardiac_meta['name'].append('lf')
            dict_cardiac_meta['unit'].append('bpm')
            dict_cardiac_meta['processing_description'].append('LF')
            dict_cardiac_meta['interface_subtype'].append('HR')
            dict_cardiac_meta['interface_name'].append('LF')
            dict_cardiac_meta['type'].append('nan')
            #
            lf_amp_data = file_['HeartRateWv']['High'][0][0][0][0]['Amp'].transpose()
            lf_amp_data = lf_amp_data.reshape(len(lf_amp_data), )  # to make an acceptable shape
            #
            dict_cardiac.update({'lf_amplitude_time': Wv_time_stamp,
                                 'lf_amplitude_data': lf_amp_data})
            dict_cardiac_meta['data_index'].append('lf_amplitude')
            dict_cardiac_meta['name'].append('lf_amplitude')
            dict_cardiac_meta['unit'].append('au')
            dict_cardiac_meta['processing_description'].append('LF amplitude')
            dict_cardiac_meta['interface_subtype'].append('AUX')
            dict_cardiac_meta['interface_name'].append('LF amplitude')
            dict_cardiac_meta['type'].append('nan')
        # else:
        #     warnings.warn(
        #         'Could NOT find the <_ProcHR.mat> from the following path... IGNORING...\n'
        #         f'{input_dir}')
        #     return 'noProcHRFile'

        # export the dict_cardiac
        df_ = pd.DataFrame.from_dict(dict_cardiac, orient='index').transpose()
        df_.set_index(list(dict_cardiac.keys())[0],
                      inplace=True)  # just to get rid of indexing columns in the out.csv file
        df_.to_csv(out_dir / 'cardiacData.csv')

        # export the dict_cardiac_meta
        df_ = pd.DataFrame(dict_cardiac_meta)
        df_.set_index('data_index', inplace=True)
        df_.to_csv(out_dir / 'cardiacData-meta.csv')

        # adding to the main-info-sheet
        mainInfoSheet.update({
            'cardiac_data': ['cardiacData.csv', 'cardiacData-meta.csv']
        })

    #
    # thermal data | yet falls under the category of processed data
    #

    if convert_thermal:

        dict_thermal = {}  # to be updated later
        dict_thermal_meta = {
            'data_index': [],
            'name': [],
            'unit': [],
            'description': [],
            'comments': [],
            'module_name': [],
            'module_description': []
        }

        thermal_file = list(input_dir.glob('*_Temperature.mat'))
        if any(thermal_file):
            file_ = loadmat(thermal_file[0])
            try:
                tracking_file = loadmat(list(input_dir.glob('*_Tracking.mat'))[0])  # required for the thermal times
            except:
                warnings.warn(
                    'Could NOT find the <_Tracking.mat> from the following path... IGNORING...\n'
                    f'{input_dir}')
                return 'noTrackingFile'

            thermal_time = np.unique(tracking_file['Thermal']['Times'][0][0])  # convention taken from Jeremy's script
            thermal_data = file_['Tail']['Max'][0][0][:, 1]
            dict_thermal.update({'tail_temperature_time': thermal_time,
                                 'tail_temperature_data': thermal_data})
            dict_thermal_meta['data_index'].append('tail_temperature')
            dict_thermal_meta['name'].append('tail temperature')
            dict_thermal_meta['unit'].append('degrees-celsius')
            dict_thermal_meta['description'].append('tail temperature')
            dict_thermal_meta['comments'].append('none')
            dict_thermal_meta['module_name'].append('thermal')
            dict_thermal_meta['module_description'].append('temperature extraction')
        else:
            warnings.warn(
                'Could NOT find the <_Temperature.mat> from the following path... IGNORING...\n'
                f'{input_dir}')
            return 'noTemperatureFile'

        # export the dict_thermal
        df_ = pd.DataFrame.from_dict(dict_thermal, orient='index').transpose()
        df_.set_index(list(dict_thermal.keys())[0],
                      inplace=True)  # just to get rid of indexing columns in the out.csv file
        df_.to_csv(out_dir / 'processedData.csv')

        # export the dict_thermal_meta
        df_ = pd.DataFrame(dict_thermal_meta)
        df_.set_index('data_index', inplace=True)
        df_.to_csv(out_dir / 'processedData-meta.csv')

        # adding to the main-info-sheet
        mainInfoSheet.update({
            'processed_data': ['processedData.csv', 'processedData-meta.csv']
        })

    #
    # events
    #

    dict_events = {}  # to be updated later
    dict_events_meta = {
        'data_index': [],
        'name': [],
        'unit': [],
        'description': [],
        'comments': [],
        'excitation_lambda': [],
        'location': [],
        'rate': [],
        'device': [],
        'stim_type': [],
    }

    events_file = list(input_dir.glob('complementary_exports/*_Events.mat'))
    if any(events_file):
        file_ = loadmat(events_file[0])
        # pure tone:
        event_range = file_['Stimulus_Data']['Tone'][0][0]['pureTone_times'][0][0]
        if np.any(event_range):
            # # to save in the conventional way to be fed into the interval_series
            # range_list = [f'[{event_range[i, 0]}, {event_range[i, 1]}]' for i in range(len(event_range))]
            # dict_events.update({'pureTone_time': range_list,  # range_list may need to be converted into an np.array
            #                     'pureTone_data': [np.nan for i in range(len(range_list))]})
            # # to be fed to timeSeries
            event_time = []
            event_data = []
            for i in range(len(event_range)):
                event_time.extend([event_range[i, 0], event_range[i, 1]])
                event_data.extend([1, -1])  # 1 indicates the start and -1 indicates end of the period
            dict_events.update({'pureTone_time': event_time,  # range_list may need to be converted into an np.array
                                'pureTone_data': event_data})
            dict_events_meta['data_index'].append('pureTone')
            dict_events_meta['name'].append('pure tone')
            dict_events_meta['unit'].append('na')
            dict_events_meta['description'].append('pure tone stimulation played in specific intervals of the session. '
                                                   'in the column data: 1 and -1 indicate the start and end of a '
                                                   'period of event respectively.')
            dict_events_meta['comments'].append('none')
            dict_events_meta['excitation_lambda'].append('nan')
            dict_events_meta['location'].append('nan')
            dict_events_meta['rate'].append('nan')
            dict_events_meta['device'].append('nan')
            dict_events_meta['stim_type'].append('context')
        # white noise:
        event_range = file_['Stimulus_Data']['Noise'][0][0]['whiteNoise_times'][0][0]
        if np.any(event_range):
            # # to save in the conventional way to be fed into the interval_series
            # range_list = [f'[{event_range[i, 0]}, {event_range[i, 1]}]' for i in range(len(event_range))]
            # dict_events.update({'whiteNoise_time': range_list,  # range_list may need to be converted into an np.array
            #                     'whiteNoise_data': [np.nan for i in range(len(range_list))]})
            # # to be fed to timeSeries
            event_time = []
            event_data = []
            for i in range(len(event_range)):
                event_time.extend([event_range[i, 0], event_range[i, 1]])
                event_data.extend([1, -1])  # 1 indicates the start and -1 indicates end of the period
            dict_events.update({'whiteNoise_time': event_time,  # range_list may need to be converted into an np.array
                                'whiteNoise_data': event_data})
            dict_events_meta['data_index'].append('whiteNoise')
            dict_events_meta['name'].append('white noise')
            dict_events_meta['unit'].append('na')
            dict_events_meta['description'].append(
                'white noise stimulation played in specific intervals of the session. in the column data: 1 and -1 '
                'indicate the start and end of a period of event respectively.')
            dict_events_meta['comments'].append('none')
            dict_events_meta['excitation_lambda'].append('nan')
            dict_events_meta['location'].append('nan')
            dict_events_meta['rate'].append('nan')
            dict_events_meta['device'].append('nan')
            dict_events_meta['stim_type'].append('context')
        # shock:
        event_range = file_['Stimulus_Data']['Shock'][0][0]['shock_times'][0][0]
        if np.any(event_range):
            # # to save in the conventional way to be fed into the interval_series
            # range_list = [f'[{event_range[i, 0]}, {event_range[i, 1]}]' for i in range(len(event_range))]
            # dict_events.update({'shock_time': range_list,  # range_list may need to be converted into an np.array
            #                     'shock_data': [10 for i in range(len(range_list))]})  #TEST 10
            # # to be fed to timeSeries
            event_time = []
            event_data = []
            for i in range(len(event_range)):
                event_time.extend([event_range[i, 0], event_range[i, 1]])
                event_data.extend([1, -1])  # 1 indicates the start and -1 indicates end of the period
            dict_events.update({'shock_time': event_time,  # range_list may need to be converted into an np.array
                                'shock_data': event_data})
            dict_events_meta['data_index'].append('shock')
            dict_events_meta['name'].append('shock')
            dict_events_meta['unit'].append('na')
            dict_events_meta['description'].append(
                'electrical shock stimulation exerted in specific intervals of the session. in the column data: 1 and -1'
                ' indicate the start and end of a period of event respectively.')
            dict_events_meta['comments'].append('none')
            dict_events_meta['excitation_lambda'].append('nan')
            dict_events_meta['location'].append('nan')
            dict_events_meta['rate'].append('nan')
            # although the device is the 'Stimulus isolator' but the TimeSeries does not get a field named device
            dict_events_meta['device'].append('nan')
            dict_events_meta['stim_type'].append('context')
        # opto:
        event_range = file_['Stimulus_Data']['Opto'][0][0]['opto_times'][0][0]
        if np.any(event_range):
            # # to save in the conventional way to be fed into the interval_series
            # range_list = [f'[{event_range[i, 0]}]' for i in range(len(event_range))]
            # dict_events.update({'opto_time': range_list,  # range_list may need to be converted into an np.array
            #                     'opto_data': [np.nan for i in range(len(range_list))]})
            # # to be fed to timeSeries
            event_time = []
            event_data = []
            for i in range(len(event_range)):
                event_time.append(event_range[i, 0])
                event_data.append(1)  # 1 indicates the start and -1 indicates end of the period | no such data at DCL
            dict_events.update({'opto_time': event_time,  # range_list may need to be converted into an np.array
                                'opto_data': event_data})
            dict_events_meta['data_index'].append('opto')
            dict_events_meta['name'].append('opto')
            dict_events_meta['unit'].append('nan')
            dict_events_meta['description'].append(
                'optogenetics stimulation applied in specific intervals of the session. in the column data: 1 and -1 '
                'indicate the start and end of a period of event respectively.')
            comments_ = file_['Stimulus_Data']['Opto'][0][0]['comments'][0][0][0]
            dict_events_meta['comments'].append(comments_)
            ex_lam = file_['Stimulus_Data']['Opto'][0][0]['excitation_lambda'][0][0][0]
            dict_events_meta['excitation_lambda'].append(ex_lam)
            ex_loc = file_['Stimulus_Data']['Opto'][0][0]['excitation_location'][0][0][0]
            dict_events_meta['location'].append(ex_loc)
            dict_events_meta['rate'].append('nan')
            dict_events_meta['device'].append('Ce:YAG Laser diode')  # the device for optogenetics
            dict_events_meta['stim_type'].append('ogen')

        # export the dict_events
        df_ = pd.DataFrame.from_dict(dict_events, orient='index').transpose()
        df_.set_index(list(dict_events.keys())[0],
                      inplace=True)  # just to get rid of indexing columns in the out.csv file
        df_.to_csv(out_dir / 'stimulusData.csv')

        # export the dict_thermal_meta
        df_ = pd.DataFrame(dict_events_meta)
        df_.set_index('data_index', inplace=True)
        df_.to_csv(out_dir / 'stimulusData-meta.csv')

        # adding to the main-info-sheet
        mainInfoSheet.update({
            'stimulation_data': ['stimulusData.csv', 'stimulusData-meta.csv']
        })

    # else:
        # warnings.warn(
        #     'Could NOT find the <_Events.mat> from the following path... IGNORING...\n'
        #     f'{input_dir}')
        # return 'noEventsFile'  # commented this; since it is not important if we're gonna have events or not

    #
    # image series data | to be addressed externally
    #

    images_file = list(input_dir.glob(f'*_{paradigm}.AVI'))
    # print(f'*_{paradigm}.AVI: {images_file}')
    if any(images_file):
        dict_image = {
            'name': 'behavior_recording',
            'description': 'video of the behaving mouse in this session',
            'unit': 'na',
            # 'external_file': '/recordings',  # for the relative path of the video relative to the .nwb file
            'external_file': images_file[0],  # for the absolute path | to be saved and changed later in the main func
            'starting_time': 0.0,
            'rate': 30.0,
            'device': 'Pike camera'
        }
        df_ = pd.DataFrame(dict_image, index=[0])  # to pass all as scalars | only one video file per session
        df_.to_csv(out_dir / 'images-meta.csv')
        # adding to the main-info-sheet
        mainInfoSheet.update({
            'images_information': ['', 'images-meta.csv']
        })

    df_ = pd.DataFrame(mainInfoSheet)
    df_.set_index('data/meta', inplace=True)
    df_.to_csv(out_dir / 'main-info-sheet.csv')

    return 'conversionSuccessful'
