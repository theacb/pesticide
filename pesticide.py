import maya.standalone as mcs
import logging
import time
import getpass
import sys
import os
import pesticideClasses as pc


def get_log_file(osx_path, win_path):
    """
    Gets a log file depending on your OS

    :param osx_path: Path using OSX mounting structure
    :param win_path: Path using windows mounting structure
    :return: The name of the log file
    """
    if sys.platform == "darwin":
        # OS X
        log_folder_path = osx_path

    elif sys.platform == "win32":
        # Windows...
        log_folder_path = win_path

    else:
        raise OSError('Unsupported Operating System')

    log_name = "lettuce_{0}-{1}.log".format(getpass.getuser(),
                                            time.strftime("%y%m%d-%H.%M.%S")
                                            )

    return os.path.normpath(os.path.join(log_folder_path, log_name))


def setup_log():
    """
    Sets up logging to a file
    :return: the logging object
    """
    osx_log_path = '/Volumes/digm_anfx/SPRJ_cgbirds/_production/scripts/logs/pesticide'
    win_log_path = '//awexpress.westphal.drexel.edu/digm_anfx/SPRJ_cgbirds/_production/scripts/logs/pesticide'

    # Log setup
    lg = logging.getLogger("pesticide")
    lg.setLevel(eval('logging.DEBUG'))

    fh = logging.FileHandler(get_log_file(osx_log_path, win_log_path))
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    fh.setFormatter(formatter)
    lg.addHandler(fh)
    lg.info("pesticide Starting")

    return lg


def get_ma_files(directory):
    flg = logging.getLogger("pesticide.get_ma_files")

    flg.info("Looking for Maya Ascii Files in {}".format(directory))

    found_files = []

    for root, dirs, files in os.walk(directory, topdown=False):
        for name in dirs:
            flg.debug("Directory: {}".format(os.path.join(root, name)))
        for name in files:
            if name.endswith('.ma'):
                ma_file = pc.FileName(name, root)
                flg.debug("File: {}".format(ma_file.get_name()))
                found_files.append(ma_file)

    return found_files


def main():
    flg = setup_log()

    search_dir = '//awexpress.westphal.drexel.edu/digm_anfx/SPRJ_cgbirds/_production/assets/environment'

    # Starts interpreter
    mcs.initialize(name='python')
    flg.info("Maya Initialized")

    files = get_ma_files(os.path.normpath(search_dir))

    mcs.uninitialize()
    flg.info("Maya uninitialized")

if __name__ == "__main__":
    main()
