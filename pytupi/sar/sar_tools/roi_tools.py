
import numpy as np


def fiil_in_lower_regions(roi, value_th=5):
    filter_selector = roi > value_th
    m = np.mean(roi[filter_selector])
    roi[np.logical_not(filter_selector)] = m
