import maya.standalone
import logging
import time
import getpass
import sys
import os


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

# Starts interpreter

maya.standalone.initialize(name='python')

lg = setup_log()

maya.standalone.uninitialize()
