# dcl2nwb [Python] package for automated conversion of DCL data
This repository contains the codes to convert acquired and processed data from Defense Circuits Lab (DCL) into NWB standard format.

## Description
Although this package is built to primarily suit the experimental data of DCL laboratory, mainly concerned with behavioral/neurophysiological evaluation of the mice under conditioned/induced fear and anxiety, it is easily extendable for the most generalized purpose of any other lab. This pipeline is based on the intiative of `csv2nwb` [find here](https://github.com/Hamidreza-Alimohammadi/csv2nwb.git), utilizing simple while structured csv tables as bridge elements to connect the user with the PyNWB API. Here, the two modules of `./dcl2nwb/mainBase/integration_from_csv.py` and `./dcl2nwb/utilBase/session2csv.py` are in fact specific to the Lab's specific way of storing data and no information or expertise on PyNWB would be required, whatsoever, to adjust these modules. 

The main conversion basis is in fact this module `./dcl2nwb/mainBase/base_func_sheet.py`, which is required to be only set once for the specific needs of one laboratory. This pipeline is designed to make batch conversions of all the relevant sessions acquired in the course of a specific project/research. To this end, the idea is to prepare a list of all sessions in a table -an instance of which exists here `./data/test_example/sessionsList.csv`, then feed it to the pipeline to search for unique sessions and start the conversion. Note that in the example of the sessionsList.csv, one finds the minimum information on a session which can point to one unique recording on the drive, which in the case of the DCL storage conventions, this unique pointer can be constructed using a Line, MouseID, Date and Paradigm.

## Using
To start using the package:
1.  I recommend to set up a new [conda environment](https://docs.conda.io/en/latest/miniconda.html) with the following dependencies:

* pynwb==2.5.0
* python==3.12.0
* ndx-ecg==0.1.0 (https://pypi.org/project/ndx-ecg/)

2. install the dcl2nwb package from this repository by simply cloning and installing it locally,
```
git clone https://github.com/Defense-Circuits-Lab/dcl2nwb.git

pip install .
```
while in the cloned directory.

3. now, the package should be installed in your environment, start a python session and simply start with:
```
from dcl2nwb import main

main.generate_templates()
```
this would generate the templates folder in `./data` containing the pre-structured tables and for all sessions these files should be updated separately -as will be carried out by `session2csv` module.

4. get started with the conversion:
```
main.start_conversion()
```
an interactive dialog-box would appear to choose the root directory of the experiment containing all the sessions, then another box to choose the outgoing directory into which the conversions (along with scan and conversion report logs) will be saved. The last dialog would ask you to choose the `sessionsList.csv` and there you go! wait for the conversions to complete and the step2step status will be printed out (color-codedly).

## Author
* Hamidreza Alimohammadi (alimohammadi.hamidreza@gmail.com)

## Version History
* 0.1.0


