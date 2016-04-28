
import cPickle as pickle
import bz2
import contextlib


def create_collection(file_to_save, title, desc, info, data):
    """ Create a collection in file_to_save with a collection:
        - title: The title of the collection
        - desc: A description string
        - info: A dictionary with information
        - data: the collection data
    """
    collection_data = {'TITLE': title, 'DESC': desc, 'INFO': info, 'DATA': data}
    with contextlib.closing(bz2.BZ2File(file_to_save, 'wb')) as f:
        pickle.dump(collection_data, f, pickle.HIGHEST_PROTOCOL)


def load_collection(file_to_load):
    """ Load file file_to_load and return its collection, where:
        collection_data = {'TITLE': title, 'DESC': desc, 'INFO': info, 'DATA': data}
    """
    with contextlib.closing(bz2.BZ2File(file_to_load, 'rb')) as f:
        collection_data = pickle.load(f)
    return collection_data

