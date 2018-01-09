__author__ = "Christian Kongsgaard"
__license__ = "MIT"
__version__ = "0.0.1"

# -------------------------------------------------------------------------------------------------------------------- #
# IMPORTS

# Modules:
import os
import shutil

# RiBuild Modules:


# -------------------------------------------------------------------------------------------------------------------- #
# TEST HELPER FUNCTIONS

def setup_test_folders():
    default_path = os.path.dirname(os.path.realpath(__file__))

    test_dir = default_path + '/test_dir'
    test_dir_source = default_path + '/test_dir/source'
    test_dir_test = default_path + '/test_dir/test'

    if not os.path.isdir(test_dir):
        os.mkdir(test_dir)
    if not os.path.isdir(test_dir_source):
        os.mkdir(test_dir_source)
    if not os.path.isdir(test_dir_test):
        os.mkdir(test_dir_test)

    return test_dir_test, test_dir_source


def unzip_with_test_folder_setup(zip_file):
    test_dir_test, test_dir_source = setup_test_folders()

    default_path = os.path.dirname(os.path.realpath(__file__))
    files_dir = default_path + '/test_files'
    shutil.unpack_archive(files_dir + '/' + zip_file, test_dir_source)

    return test_dir_test, test_dir_source


def clean_up_test_folders():
    test_dir = os.path.dirname(os.path.realpath(__file__)) + '/test_dir'
    shutil.rmtree(test_dir)
