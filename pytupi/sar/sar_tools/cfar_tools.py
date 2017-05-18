
import numpy as np
from scipy import ndimage
from scipy import signal


def _create_bg_window(bg_window_size, guard_window_size=None):
    if not guard_window_size:
        guard_window_size = bg_window_size // 3
    bg_window = np.ones(shape=(bg_window_size, bg_window_size))
    bg_window[(bg_window_size // 2 - guard_window_size // 2):(bg_window_size // 2 + guard_window_size // 2), :] = 0
    bg_window[:, (bg_window_size // 2 - guard_window_size // 2):(bg_window_size // 2 + guard_window_size // 2)] = 0
    return bg_window


def _create_target_window(bg_window_size, target_window_size):
    target_window = np.zeros(shape=(bg_window_size, bg_window_size))
    target_window[(bg_window_size // 2 - target_window_size // 2):(bg_window_size // 2 + target_window_size // 2),
                  (bg_window_size // 2 - target_window_size // 2):(bg_window_size // 2 + target_window_size // 2)] = 1
    return target_window


def _clear_border(_roi, border_size):
    _roi[0:border_size, :] = 0.0
    _roi[-border_size:, :] = 0.0
    _roi[:, 0:border_size] = 0.0
    _roi[:, -border_size:] = 0.0
    return _roi


def cfar_roi(roi):

    roi_target = roi.copy()
    roi_bg = roi.copy()

    # Truncate background values
    img_mean = np.mean(roi)
    img_std = np.std(roi)
    roi_bg[roi > 5.0*img_mean] = 5.0*img_mean
    bg_window_size = 64
    border_size = bg_window_size/2
    target_window_size = 6
    bg_window = _create_bg_window(bg_window_size)
    target_window = _create_target_window(bg_window_size, target_window_size)

    # CFAR
    cfar_img = np.zeros(shape=roi_target.shape)
    mean_cfar = signal.fftconvolve(roi_bg, bg_window, mode='same') / np.sum(bg_window)
    mean_cfar = _clear_border(mean_cfar, border_size)
    sigma_cfar = signal.fftconvolve(abs(roi_bg - mean_cfar), bg_window, mode='same') / np.sum(bg_window)
    sigma_cfar = _clear_border(sigma_cfar, border_size)
    target_cfar = signal.fftconvolve(roi_target, target_window, mode='same') / np.sum(target_window)
    target_cfar = _clear_border(target_cfar, border_size)
    th_scale = 10.0
    th_matrix = img_mean/10.0 + mean_cfar + th_scale*sigma_cfar
    cfar_img[target_cfar > th_matrix] = 1

    # Detections
    s = np.ones(shape=(3, 3))
    all_labels = ndimage.measurements.label(cfar_img, structure=s)
    label_list = np.unique(all_labels[0])
    inv_detections = ndimage.measurements.center_of_mass(cfar_img, all_labels[0], label_list[1:])
    detections = [(int(x[1]), int(x[0])) for x in inv_detections]
    return detections


def filter_detections(sar_sensor, gshhs_map, global_detections):
    filtered_detections = []
    buffer_land = 500
    for det in global_detections:
        is_land = False
        for a,b in [(-1,-1), (-1,1), (1,-1), (1,1), (-1,0), (1,0), (0,-1), (0,1)]:
            absolute_x = det[0] + a*buffer_land
            absolute_y = det[1] + b*buffer_land
            lat, lon = sar_sensor.getGeoLocation(absolute_x, absolute_y)
            is_land = is_land or gshhs_map.isOverLand([lon, lat])
            if is_land:
                break
        if not is_land:
            filtered_detections.append(det)
    return filtered_detections
