import os
import shutil


def file_structures_setup():
    default_path = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\delphin_6_automation\pytest'
    files_dir = default_path + '/test_files'
    test_dir_source = default_path + '/test_dir/source'
    test_dir_test = default_path + '/test_dir/test'
    os.mkdir(test_dir_source)
    os.mkdir(test_dir_test)
    shutil.unpack_archive(files_dir + '/5a25121f5d94600c683b82bd.zip', test_dir_source)

    return test_dir_test, test_dir_source


def clean_up():
    test_dir = r'C:\Users\ocni\PycharmProjects\delphin_6_automation\delphin_6_automation\pytest\test_dir'
    shutil.rmtree(test_dir)