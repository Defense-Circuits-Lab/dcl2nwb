import runpy as rp
from pathlib import Path
from . import path_id  # to get the initialization of the directory


def start_conversion():
    global curr_
    path_ = curr_ / Path('mainBase/nwb_conversion_main.py')
    rp.run_path(path_)


def generate_templates():
    global curr_
    path_ = curr_ / Path('utilBase/template_generator.py')
    rp.run_path(path_)


curr_ = Path(path_id.__file__).parent  # dynamic path of the main.py container folder

