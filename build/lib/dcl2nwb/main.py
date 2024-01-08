import runpy as rp
import os


def start_conversion():
    global curr_
    path_ = os.path.join(curr_, 'mainBase/nwb_conversion_main.py')
    rp.run_path(path_)


def generate_templates():
    global curr_
    path_ = os.path.join(curr_, 'utilBase/template_generator.py')
    rp.run_path(path_)


curr_ = '/'.join(__file__.split('/')[:-1])  # dynamic path of the main.py

