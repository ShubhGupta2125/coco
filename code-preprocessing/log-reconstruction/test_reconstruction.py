# A series of tests to check whether the python scripts of log-reconstruction perform correctly.
# Start the tests by writing
# py.test
# in a terminal window

from os.path import dirname, abspath, join, exists
from os import walk, remove, rmdir, chdir, chmod, mkdir


def prepare_reconstruction_data():
    """
    Unpacks the data to the test-data folder.
    """
    import urllib
    import tarfile
    cleanup_reconstruction_data()
    data_folder = abspath(join(dirname(__file__), 'test-data'))
    if not exists(abspath(join(data_folder, 'archives-input'))) or not exists(
            abspath(join(data_folder, 'reconstruction'))):
        cleanup_reconstruction_data(True)
        chdir(abspath(dirname(__file__)))
        data_url = 'http://dis.ijs.si/tea/tmp/log-reconstruction-test-data.tgz'
        filename, headers = urllib.urlretrieve(data_url)
        tar_file = tarfile.open(filename)
        tar_file.extractall()

    for root, dirs, files in walk(data_folder, topdown=False):
        for name in files:
            # Change file permission so it can be deleted
            chmod(join(root, name), 0777)


def cleanup_reconstruction_data(delete_all=False):
    """
    Deletes the exdata folder. If delete_all is True, deletes also the test-data folder.
    """

    if exists(abspath(join(dirname(__file__), 'exdata'))):
        for root, dirs, files in walk(abspath(join(dirname(__file__), 'exdata')), topdown=False):
            for name in files:
                remove(join(root, name))
            for name in dirs:
                rmdir(join(root, name))
        rmdir(abspath(join(dirname(__file__), 'exdata')))

    if delete_all and exists(abspath(join(dirname(__file__), 'test-data'))):
        for root, dirs, files in walk(abspath(join(dirname(__file__), 'test-data')), topdown=False):
            for name in files:
                remove(join(root, name))
            for name in dirs:
                rmdir(join(root, name))
        rmdir(abspath(join(dirname(__file__), 'test-data')))


def run_log_reconstruct():
    """
    Tests whether log_reconstruct() from log_reconstruct.py works correctly for the given input.
    """
    from log_reconstruct import log_reconstruct
    from cocoprep.archive_load_data import parse_range
    import filecmp

    base_path = dirname(__file__)
    log_reconstruct(abspath(join(base_path, 'test-data', 'archives-input')),
                    'reconstruction',
                    'RECONSTRUCTOR',
                    'A test for reconstruction of logger output',
                    parse_range('1-55'),
                    parse_range('1-10'),
                    parse_range('2,3,5,10,20,40'))

    for root, dirs, files in walk(abspath(join(base_path, 'exdata', 'reconstruction')), topdown=False):
        for name in files:
            assert filecmp.cmp(abspath(join(root, name)),
                               abspath(join(root, name)).replace('exdata', 'test-data'))


def run_merge_lines():
    """
    Tests whether merge_lines_in() from merge_lines_in_info_files.py works correctly for the given input.
    """
    from merge_lines_in_info_files import merge_lines_in
    import shutil
    import filecmp

    base_path = dirname(__file__)
    in_path = abspath(join(base_path, 'exdata', 'reconstruction'))
    out_path = abspath(join(base_path, 'exdata', 'reconstruction-merged'))
    mkdir(out_path)

    for root, dirs, files in walk(in_path, topdown=False):
        for name in files:
            if name.endswith('.info'):
                shutil.copyfile(abspath(join(in_path, name)), abspath(join(out_path, name)))
                merge_lines_in(abspath(join(root, name)), in_path, out_path)

    for root, dirs, files in walk(out_path, topdown=False):
        for name in files:
            assert filecmp.cmp(abspath(join(root, name)),
                               abspath(join(root, name)).replace('exdata', 'test-data'))


def test_all():
    """
    Runs a number of tests to check whether the python scripts of log-reconstruction perform correctly.
    The name of the method needs to start with "test_" so that it gets picked up by py.test.
    """

    prepare_reconstruction_data()

    run_log_reconstruct()

    run_merge_lines()

    cleanup_reconstruction_data()


if __name__ == '__main__':
    test_all()
