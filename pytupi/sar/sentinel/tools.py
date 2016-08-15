

import os
import fnmatch
from collections import defaultdict


def search_images(dir_path):

    s_files = []
    for dirpath, dirnames, files in os.walk(dir_path):
        # Add compressed files
        for f in fnmatch.filter(files, 'S1A_*.zip'):
            s_file = os.path.join(dirpath, f)
            s_files.append(s_file)
        # Add project folders
        for f in fnmatch.filter(dirnames, 'S1A_*.SAFE'):
            s_file = os.path.join(dirpath, f)
            s_files.append(s_file)

    s1_files_map = defaultdict(list)
    for f in s_files:
        base_name = os.path.basename(f)
        s1_name = base_name.split('.')[0]
        s1_files_map[s1_name].append(f)

    return s1_files_map


