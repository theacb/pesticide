import maya.standalone as mcs
import maya.cmds as mc
import logging
import sys
import os

from time import strftime
from getpass import getuser

import pesticideclasses as pc


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

    log_name = "lettuce_{0}-{1}.log".format(getuser(),
                                            strftime("%y%m%d-%H.%M.%S")
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


def search_file(f, bad_types):
    flg = logging.getLogger("pesticide.search_file")

    flg.info("Looking in file: {}".format(f.get_name()))

    mc.file(f.get_path(), open=True)

    flg.info("Getting Node List")
    nodes = mc.ls(l=True)

    flg.info("Checking Nodes")
    bad_nodes = check_nodes(nodes, bad_types)

    flg.info("Checking Nodes")
    for n in bad_nodes:
        f.append_bad_node(n)

    return f


def check_nodes(nodes, bad_types):
    flg = logging.getLogger("pesticide.check_nodes")

    flg.info("Sorting Nodes")
    nodes.sort()
    bad_types.sort()

    bad_nodes = []

    flg.debug("Locating Alphabetical Indices")
    index_dict = find_alphabetical_index(nodes)

    flg.debug("Checking for bad nodes that are definitely not present")
    for n in bad_types:
        if not n.lower()[0] in index_dict:
            flg.debug("No nodes start with {0}, removing: {1}".format(n.lower()[0], n))
            bad_types.remove(n)

    for n in bad_types:
        flg.debug("Looking for {} nodes in scene".format(n))
        cur_char = n.lower()[0]
        ind = (index_dict[cur_char])[0]

        loop = True

        while loop:
            if cur_node.lower()[0] != cur_char:
                break
            cur_node = nodes[ind]

            if cur_node == n:
                flg.debug("{0} is of type {1}".format(cur_node, n))
                bad_nodes.append(cur_node)

            ind += 1

    flg.info("Returning {} bad nodes".format(len(bad_nodes)))
    return bad_nodes


def find_alphabetical_index(nodes):
    flg = logging.getLogger("pesticide.find_alphabetical_index")

    nodes.sort()
    index_dict = {}

    possible_chars = list("0123456789_abcdefghijklmnopqrstuvwxyz")
    master_cur_char = 0
    i = 0

    flg.debug("Getting alphabetical index of node list")
    for n in nodes:
        flg.debug("Node: {}".format(n))
        this_cur_char = n.lower()[0]
        for c in range(master_cur_char, len(possible_chars)):
            if possible_chars[c] == this_cur_char:
                flg.debug("Node {0} has the first name to begin with {1} at index {2}".format(n, possible_chars[c], i))
                index_dict[possible_chars[c]] = [i]
                master_cur_char = c + 1
                break
        i += 1

    flg.debug("Returning dictionary containing {} entries".format(len(index_dict)))
    return index_dict


def bad_types_list():
    return ['rman']


def compile_results(results):
    return results


def main():
    flg = setup_log()

    search_dir = '//awexpress.westphal.drexel.edu/digm_anfx/SPRJ_cgbirds/_production/assets/environment\elements\curves'

    # Starts interpreter
    mcs.initialize(name='python')
    flg.info("Maya Initialized")

    files = get_ma_files(os.path.normpath(search_dir))

    results = []

    flg.info("Getting List of Unwanted Nodes")
    bad_types = bad_types_list()

    flg.info("Searching Files")
    for f in files:
        results.append(search_file(f, bad_types))

    flg.info("Compiling results")
    compile_results(results)

    mcs.uninitialize()
    flg.info("Maya uninitialized")

if __name__ == "__main__":
    main()
