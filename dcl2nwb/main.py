import runpy as rp
from pathlib import Path


def start_conversion():
    global curr_
    path_ = curr_ / Path('mainBase/nwb_conversion_main.py')
    rp.run_path(path_)


def generate_templates():
    global curr_
    path_ = curr_ / Path('utilBase/template_generator.py')
    rp.run_path(path_)


curr_ = Path(__file__).parents[0]  # dynamic path of the main.py container folder

