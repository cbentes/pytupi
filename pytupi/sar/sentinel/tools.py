

import os
import fnmatch
import zipfile
from collections import defaultdict

import xmltodict


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


def get_basic_info_from_compressed_file(s1_compressed_file):

    zfile = zipfile.ZipFile(s1_compressed_file)
    files = sorted(zfile.namelist())
    base_name = files[0]
    manifest_file = base_name+'manifest.safe'
    with zfile.open(manifest_file, 'r') as f:
        manifest_tree = xmltodict.parse(f.read())

    basic_info = {}
    basic_info['name'] = base_name[:-1] # remove last / in the name

    for d in manifest_tree['xfdu:XFDU']['metadataSection']['metadataObject']:

        if d['@ID'] == 'measurementOrbitReference':
            orbit_ref = d['metadataWrap']['xmlData']['safe:orbitReference']
            basic_info['OrbitReference'] = orbit_ref['safe:extension']['s1:orbitProperties']['s1:pass']
        if d['@ID'] == 'acquisitionPeriod':
            ac_period = d['metadataWrap']['xmlData']['safe:acquisitionPeriod']
            basic_info['startTime'] = ac_period['safe:startTime']
            basic_info['stopTime'] = ac_period['safe:stopTime']
        if d['@ID'] == 'measurementFrameSet':
            frame = d['metadataWrap']['xmlData']['safe:frameSet']['safe:frame']
            basic_info['coordinates'] = frame['safe:footPrint']['gml:coordinates']

    return basic_info
