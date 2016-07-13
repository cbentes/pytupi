import os
import urllib
import gzip
import cPickle as pickle


class Loader:

    def __init__(self, datasets, cache_folder):
        self._datasets = datasets
        self._cache_folder = cache_folder

    def get(self, dataset_name):
        dataset = self._datasets[dataset_name]
        file_name = dataset['name']
        file_path = os.path.join(self._cache_folder, file_name)
        uri = dataset['uri']
        if not os.path.exists(file_path):
            print("Downloading {0} into cache folder ...".format(file_name))
            urllib.urlretrieve(uri, file_path)
        with gzip.open(file_path, 'rb') as f:
            data = pickle.load(f)
        return data
