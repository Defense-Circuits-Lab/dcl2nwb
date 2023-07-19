import pandas as pd
import numpy as np
from pathlib import Path
import os


# create out_dir based on current path of the template_generator module
out_dir = Path(__file__).parents[2] / 'data/templates'
if not os.path.exists(out_dir):
    os.mkdir(out_dir)

#  naming convention in each folder / important
#
dict_ = {
    'data/meta': ['mainData', 'metaData'],
    'session_information': ['', 'session-meta'],
    'subject_information': ['', 'subject-meta'],
    'devices_information': ['', 'devices-meta'],
    'acquisition': ['acquisition', 'acquisition-meta'],
    'processed_data': ['processedData', 'processedData-meta'],
    'behavioral_data': ['behavioralData', 'behavioralData-meta'],
    'stimulation_data': ['stimulusData', 'stimulusData-meta'],
}
df_ = pd.DataFrame(dict_)
df_.set_index('data/meta', inplace=True)
df_.to_csv(os.path.join(out_dir, 'main-info-sheet.csv'))


# to generate nwb file
dict_ = {
    'session_description': 'write a description',
    'identifier': 'mouseID:dayX',
    'start_date': '2023, 5, 22',
    'start_time': '14, 50, 00',
    'location': 'Europe/Berlin',
    'session_id': 'sessionID',
    'experimenter': 'HMDRZAA',
    'lab': 'DCL',
    'institution': 'UKW',
    'experiment_description': 'write a human understandable statement!',
    'related_publications': 'DOI:X',
    'keywords': 'X, Y, Z'
}
df_ = pd.DataFrame(dict_, index=[0])  # to save all scalars | pandas
df_.to_csv(os.path.join(out_dir, 'session-meta.csv'))


# to define a subject
dict_ = {
    'description': 'write a description',
    'species': 'X',
    'genotype': 'X',
    'sex': 'X',
    'age': 'X',
}
df_ = pd.DataFrame(dict_, index=[0])  # to save all scalars | pandas
df_.to_csv(os.path.join(out_dir, 'subject-meta.csv'))


# devices meta
dict_ = {
    'name': ['X', 'ogen_device_name_1', 'ogen_device_name_2'],
    'manufacturer': ['X', 'ogen_1', 'ogen_2'],
    'description': ['X', 'ogen_1', 'ogen_2'],
}
df_ = pd.DataFrame(dict_)
df_.to_csv(os.path.join(out_dir, 'devices-meta.csv'))


# acquisition
dict_ = {
    'acquisition1_time': np.linspace(0, 1, 15),
    'acquisition1_data': np.random.uniform(0, 1, size=[15, ]) * np.random.randint(0, 2, size=[15, ]),
    'acquisition2_time': np.linspace(0, 1, 25),
    'acquisition2_data': np.random.uniform(0, 1, size=[25, ]) * np.random.randint(0, 2, size=[25, ]),
    'acquisition3_time': np.linspace(0, 1, 10),
    'acquisition3_data': np.random.uniform(0, 1, size=[10, ]) * np.random.randint(0, 2, size=[10, ]),
}
df_ = pd.DataFrame.from_dict(dict_, orient='index').transpose()
df_.set_index('acquisition1_time', inplace=True)  # just to get rid of indexing columns in the out.csv file
df_.to_csv(os.path.join(out_dir, 'acquisition.csv'))
#
dict_ = {
    'data_index': ['acquisition1', 'acquisition2', 'acquisition3'],
    'name': ['X', 'Y', 'Z'],
    'unit': ['X', 'Y', 'Z'],
    'description': ['X', 'Y', 'Z'],
    'comments': ['X', 'Y', 'Z']
}
df_ = pd.DataFrame(dict_)
df_.set_index('data_index', inplace=True)
df_.to_csv(os.path.join(out_dir, 'acquisition-meta.csv'))


# processed data
dict_ = {
    'processedData1_time': np.linspace(0, 1, 15),
    'processedData1_data': np.random.uniform(0, 1, size=[15, ]) * np.random.randint(0, 2, size=[15, ]),
    'processedData2_time': np.linspace(0, 1, 25),
    'processedData2_data': np.random.uniform(0, 1, size=[25, ]) * np.random.randint(0, 2, size=[25, ]),
    'processedData3_time': np.linspace(0, 1, 10),
    'processedData3_data': np.random.uniform(0, 1, size=[10, ]) * np.random.randint(0, 2, size=[10, ]),
}
df_ = pd.DataFrame.from_dict(dict_, orient='index').transpose()
df_.set_index('processedData1_time', inplace=True)  # just to get rid of indexing columns in the out.csv file
df_.to_csv(os.path.join(out_dir, 'processedData.csv'))
#
dict_ = {
    'data_index': ['processedData1', 'processedData2', 'processedData3'],
    'name': ['X', 'Y', 'Z'],
    'unit': ['X', 'Y', 'Z'],
    'description': ['X', 'Y', 'Z'],
    'comments': ['X', 'Y', 'Z'],
    'module_name': ['m1_names_to_be_short_only_underline_separation',
                    'm1_names_to_be_short_only_underline_separation',
                    'm2_names_to_be_short_only_underline_separation'],
    'module_description': ['m1 description', 'm1 description', 'm2 description']
}
df_ = pd.DataFrame(dict_)
df_.set_index('data_index', inplace=True)
df_.to_csv(os.path.join(out_dir, 'processedData-meta.csv'))


# behavioral data
dict_ = {
    'pos1_time': np.linspace(0, 1, 10),
    'pos1_data': np.random.uniform(-1, 1, size=[10, ]),
    'pos2_time': np.linspace(0, 1, 15),
    'pos2_data': np.random.uniform(-2, 2, size=[15, ]),
    'behavioralSeries1_time': np.linspace(0, 1, 20),
    'behavioralSeries1_data': np.random.uniform(0, 1, size=[20, ]),
    'behavioralSeries2_time': np.linspace(0, 1, 25),
    'behavioralSeries2_data': np.random.uniform(0, 1, size=[25, ]),
    'behavioralEpoch1_time': np.linspace(0, 1, 15),
    'behavioralEpoch1_data': np.random.randint(0, 2, size=[15, ]),
    'behavioralEpoch2_time': np.linspace(0, 1, 10),
    'behavioralEpoch2_data': np.random.randint(0, 2, size=[10, ])
}
df_ = pd.DataFrame.from_dict(dict_, orient='index').transpose()
df_.set_index('pos1_time', inplace=True)  # just to get rid of indexing columns in the out.csv file
df_.to_csv(os.path.join(out_dir, 'behavioralData.csv'))
#
dict_ = {
    'data_index': ['pos1', 'pos2', 'behavioralSeries1', 'behavioralSeries2',
                   'behavioralEpoch1', 'behavioralEpoch2'],
    'name': ['X', 'Y', 'A', 'B', 'C', 'D'],
    'description': ['X', 'Y', 'A', 'B', 'C', 'D'],
    'reference_frame': ['X', 'Y', 'nan', 'nan', 'nan', 'nan'],
    'unit': ['X', 'Y', 'A', 'B', 'nan', 'nan'],
    'comments': ['X', 'Y', 'A', 'B', 'C', 'D'],
    'interface_subtype': ['position', 'position', 'time_series', 'time_series',
                          'epochs', 'epochs']
}
df_ = pd.DataFrame(dict_)
df_.set_index('data_index', inplace=True)
df_.to_csv(os.path.join(out_dir, 'behavioralData-meta.csv'))


# stimulus data
dict_ = {
    'contextStim1_time': np.linspace(0, 1, 10),
    'contextStim1_data': np.random.uniform(0, 1, size=[10, ]) * np.random.randint(0, 2, size=[10, ]),
    'contextStim2_time': np.linspace(0, 1, 15),
    'contextStim2_data': np.random.uniform(0, 1, size=[15, ]) * np.random.randint(0, 2, size=[15, ]),
    'optoStim1_time': np.linspace(0, 1, 20),
    'optoStim1_data': np.random.uniform(0, 1, size=[20, ]) * np.random.randint(0, 2, size=[20, ]),
    'optoStim2_time': np.linspace(0, 1, 25),
    'optoStim2_data': np.random.uniform(0, 1, size=[25, ]) * np.random.randint(0, 2, size=[25, ])
}
df_ = pd.DataFrame.from_dict(dict_, orient='index').transpose()
df_.set_index('contextStim1_time', inplace=True)  # just to get rid of indexing columns in the out.csv file
df_.to_csv(os.path.join(out_dir, 'stimulusData.csv'))
#
dict_ = {
    'data_index': ['contextStim1', 'contextStim2', 'optoStim1', 'optoStim2'],
    'name': ['X', 'Y', 'A', 'B'],
    'unit': ['X', 'Y', 'nan', 'nan'],
    'description': ['X', 'Y', 'A', 'B'],
    'comments': ['X', 'Y', 'A', 'B'],
    'excitation_lambda': ['nan', 'nan', '0.3', '0.5'],
    'location': ['nan', 'nan', 'A', 'B'],
    'rate': ['nan', 'nan', 'A', 'B'],
    'device': ['nan', 'nan', 'ogen_device_name_1', 'ogen_device_name_2'],
    'stim_type': ['context', 'context', 'ogen', 'ogen'],
}
df_ = pd.DataFrame(dict_)
df_.set_index('data_index', inplace=True)
df_.to_csv(os.path.join(out_dir, 'stimulusData-meta.csv'))

