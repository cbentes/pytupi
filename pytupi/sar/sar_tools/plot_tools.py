
import matplotlib
matplotlib.use('Agg')
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
from matplotlib.colors import Normalize
import matplotlib.patches as patches


def plot_img(img, title='', figsize=(14, 14), plt_min=None, plt_max=None,
             color=None, save_to=None):

    plt.figure(figsize=figsize)
    if plt_min is None:
        plt_min = img.min()
    if plt_max is None:
        plt_max = 2.7*img.mean()
    if color is None:
        color = plt.gray()
    plt.imshow(img, cmap=color, norm=Normalize(vmin=plt_min, vmax=plt_max, clip=True))
    plt.xticks(())
    plt.yticks(())
    plt.xlabel(title)
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=300, bbox_inches='tight')


def plot_detections(img, detections, title='', figsize=(14, 14), plt_min=None, plt_max=None,
                    color=None, square_size=30, save_to=None):

    plt.figure(figsize=figsize)
    ax = plt.gca()
    if plt_min is None:
        plt_min = img.min()
    if plt_max is None:
        plt_max = 2.7*img.mean()
    if color is None:
        color = plt.gray()
    plt.imshow(img, cmap=color, norm=Normalize(vmin=plt_min, vmax=plt_max, clip=True))
    for det in detections:
        rect_corner = (det[0] - square_size/2, det[1] - square_size/2)
        rect = patches.Rectangle(rect_corner,square_size,square_size,linewidth=2,edgecolor='r',facecolor='none')
        ax.add_patch(rect)
    plt.xticks(())
    plt.yticks(())
    plt.xlabel(title)
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=300, bbox_inches='tight')


def plot_bbox_regions(img, bbox_list, title='', figsize=(14, 14), plt_min=None,
                      plt_max=None, color=None, save_to=None):

    plt.figure(figsize=figsize)
    ax = plt.gca()
    if plt_min is None:
        plt_min = img.min()
    if plt_max is None:
        plt_max = 2.7*img.mean()
    if color is None:
        color = plt.gray()
    plt.imshow(img, cmap=color, norm=Normalize(vmin=plt_min, vmax=plt_max, clip=True))
    for bbox in bbox_list:
        region_size_x = bbox[1] - bbox[0]
        region_size_y = bbox[3] - bbox[2]
        rect_corner = (bbox[0], bbox[2])
        rect = patches.Rectangle(rect_corner,region_size_x,region_size_y, linewidth=2,edgecolor='r',facecolor='none')
        ax.add_patch(rect)
    plt.xticks(())
    plt.yticks(())
    plt.xlabel(title)
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=300, bbox_inches='tight')


def plot_roi_frames(img, roi_frame_list, title='', figsize=(14, 14), plt_min=None,
                    plt_max=None, color=None, save_to=None):

    plt.figure(figsize=figsize)
    ax = plt.gca()
    if plt_min is None:
        plt_min = img.min()
    if plt_max is None:
        plt_max = 2.7*img.mean()
    if color is None:
        color = plt.gray()
    plt.imshow(img, cmap=color, norm=Normalize(vmin=plt_min, vmax=plt_max, clip=True))
    for r_frame in roi_frame_list:
        rect_corner = (r_frame.offset_x, r_frame.offset_y)
        rect = patches.Rectangle(rect_corner, r_frame.roi_size_x, r_frame.roi_size_y,
                                 linewidth=2,edgecolor='r',facecolor='none')
        ax.add_patch(rect)
    plt.xticks(())
    plt.yticks(())
    plt.xlabel(title)
    plt.tight_layout()
    if save_to:
        plt.savefig(save_to, dpi=300, bbox_inches='tight')
