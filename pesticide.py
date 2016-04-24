import maya.standalone as mcs
import maya.cmds as mc
import logging
import sys
import os

from time import strftime
from getpass import getuser

import pesticide_classes as pc


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

    log_name = "pesticide_{0}-{1}.log".format(getuser(),
                                              strftime("%y%m%d-%H.%M.%S")
                                              )

    return os.path.normpath(os.path.join(log_folder_path, log_name))


def setup_log(level='logging.WARNING'):
    """
    Sets up logging to a file
    :return: the logging object
    """
    osx_log_path = '/Volumes/digm_anfx/SPRJ_cgbirds/_production/scripts/logs/pesticide'
    win_log_path = '//awexpress.westphal.drexel.edu/digm_anfx/SPRJ_cgbirds/_production/scripts/logs/pesticide'

    # Log setup
    lg = logging.getLogger("pesticide")
    lg.setLevel(eval(level))

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

    mc.file(f.get_path(),
            open=True
            )

    flg.info("Getting Node List")
    nodes = mc.ls(shortNames=True)

    flg.info("Checking Nodes")
    bad_nodes = check_nodes(nodes, bad_types)

    flg.info("Checking Nodes")
    for n in bad_nodes:
        f.append_bad_node(n)

    return f


def check_nodes(nodes, bad_types):
    flg = logging.getLogger("pesticide.check_nodes")

    flg.info("Removing References")
    for n in nodes:
        if ':' in n:
            nodes.remove(n)

    flg.info("Sorting Nodes")
    nodes.sort()
    bad_types.sort()

    bad_nodes = []

    flg.debug("Locating Alphabetical Indices")
    index_dict = find_alphabetical_index(nodes)

    flg.debug("Checking for bad nodes that are definitely not present")
    for n in bad_types:
        if not n[0] in index_dict:
            flg.debug("No nodes start with {0}, removing: {1}".format(n[0], n))
            bad_types.remove(n)

    for n in bad_types:
        flg.debug("Looking for {} nodes in scene".format(n))
        cur_char = n[0]
        ind = (index_dict[cur_char])[0]

        loop = True

        while loop:
            cur_node = nodes[ind]

            if cur_node[0] != cur_char:
                break

            if n in cur_node:
                flg.debug("{0} is of type {1}".format(cur_node, n))
                bad_nodes.append(cur_node)

            ind += 1

    flg.info("Returning {} bad nodes".format(len(bad_nodes)))
    return bad_nodes


def find_alphabetical_index(nodes):
    flg = logging.getLogger("pesticide.find_alphabetical_index")

    nodes.sort()
    index_dict = {}

    possible_chars = list("0123456789_ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    master_cur_char = 0
    i = 0

    flg.debug("Getting alphabetical index of node list")
    for n in nodes:
        flg.debug("Node: {}".format(n))
        this_cur_char = n[0]
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
    return ['rman', 'renderManRISGlobals']


def compile_results(file_objects, *args):
    flg = logging.getLogger("pesticide.compile_results")

    results_for_print = []

    if len(file_objects) <= 0:
        flg.debug("No file objects passed to function")
        results_for_print.append("No Files Processed")
        return
    for f in file_objects:
        bad_nodes = f.get_bad_nodes()
        if len(bad_nodes) > 0:
            msg = "-Bad node{0} found in file: {1}".format(is_plural(bad_nodes),
                                                           f.get_name(),
                                                           )
            results_for_print.append('\r')
            results_for_print.append(msg)

            flg.warning(msg)

            line_str = " " * 4

            for b in f.get_bad_nodes():
                msg = "{0}-{1}".format(" " * 4, b)
                flg.warning(msg)
                line_str = "{0}{1}, ".format(line_str, b)
                if len(line_str) > 150:
                    results_for_print.append(line_str)
                    line_str = " " * 4

            msg = "Total: {}".format(len(bad_nodes))

            flg.warning(msg)

            results_for_print.append(msg)

        else:
            flg.debug("No bad nodes found in file: {}".format(f.get_name()))

    if len(results_for_print) <= 0:
        results_for_print.append("Searched {} files\r".format(len(file_objects)))
        results_for_print.append("No bad nodes found")
    else:
        msg = "Results:"
        results_for_print.insert(0, msg)

        msg = "Searched {} files\r".format(len(file_objects))
        flg.debug(msg)
        results_for_print.insert(0, msg)

    if len(args) > 0:
        for a in reversed(args):
            results_for_print.insert(0, a)

    return results_for_print


def is_plural(array):
    if len(array) == 1:
        return ""
    else:
        return "s"


def array_to_file(results_array, name):
    flg = logging.getLogger("pesticide.array_to_file")
    try:
        f = open(name, 'w')

        flg.debug("Writing to file: {}".format(name))
        flg.debug(f)

        for line in results_array:
            f.write("{}\r".format(line))

        f.close()
        flg.debug("Done")
    except IOError as e:
        flg.error("Unable to write results to file")
        flg.error("IO Error: {}".format(e))
        raise


def test_file(name):
    flg = logging.getLogger("pesticide.test_file")
    try:
        f = open(name, 'w')

        flg.debug("Creating file: {}".format(name))
        flg.debug(f)

        f.close()
        flg.debug("Done")
    except IOError as e:
        flg.error("Unable to create file")
        flg.error("IO Error: {}".format(e))
        raise


def gen_file_name():

    path = ""

    osx_path = '/Volumes/digm_anfx/SPRJ_cgbirds/_production/scripts/logs/pesticide'
    win_path = '//awexpress.westphal.drexel.edu/digm_anfx/SPRJ_cgbirds/_production/scripts/logs/pesticide'

    if sys.platform == "darwin":
        # OS X
        path = osx_path

    elif sys.platform == "win32":
        # Windows...
        path = win_path

    file_name = "results_{0}-{1}.txt".format(getuser(),
                                             strftime("%y%m%d-%H.%M.%S")
                                             )
    return os.path.join(path, file_name)


def main():
    start_time = strftime("%H:%M:%S")
    date = strftime("%m/%d/%y")

    flg = setup_log()

    search_dir = '//awexpress.westphal.drexel.edu/digm_anfx/SPRJ_cgbirds'

    # Starts interpreter
    mcs.initialize(name='python')
    flg.info("Maya Initialized")

    output_file_name = gen_file_name()

    files = get_ma_files(os.path.normpath(search_dir))

    results = []

    flg.info("Getting List of Unwanted Nodes")
    bad_types = bad_types_list()

    flg.info("Searching Files")
    i = 0
    for f in files:
        print("{} out of {} files".format(i, len(files)))
        results.append(search_file(f, bad_types))
        i += 1

    flg.info("Compiling results")
    comp_res = compile_results(results,
                               "Searched: {}".format(search_dir),
                               '\r',
                               "Started at {} on {}".format(start_time, date),
                               "User: {}".format(getuser()),
                               '\r',
                               '*' * 150,
                               '\r'
                               )

    array_to_file(comp_res, output_file_name)

    mcs.uninitialize()
    flg.info("Maya uninitialized")

if __name__ == "__main__":
    main()
