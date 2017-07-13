'''
Author: Andrew Mocle & Lina Tran
Date: July 13, 2017

Motion correction within a single video file.
'''
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from skimage import img_as_uint
from sklearn.preprocessing import scale
from skimage.transform import SimilarityTransform, warp


def align_video(video, thresh=1.8, cutoff=0.05, target_frame=0):
    '''
    Motion correct video to target_frame of video.
    Input:
        - video: numpy array of video dim(frame, x, y)
        - threshold: float, for selecting background to fit, default=1.8
        - cutoff: float, spatial frequency of cells to remove, default=0.05
        - target_frame: int, reference frame to register other frames to, default=0
    Output:
        numpy array of registered video
    '''
    print('Filtering')
    video_spatial = spatial_lp_filter(video, 3, cutoff)

    target = video_spatialtarget_frame, :, :]
    video_reg = np.zeros_like(video)

    for frame in range(video.shape[0]):
        tx, ty = align_frame(target, video[frame, :, :], thresh)
        video_reg[frame, :, :] = img_as_uint(translate(video[frame, :, :], -tx, -ty))

    return video_reg


def align_frame(target, img, thresh):
    '''
    Align img frame to target frame.
    Input:
        - target: int, reference frame to register img frame to
        - img: int, frame to register to target
        - thresh: float, threshold for selecting background to filtfilt
    Output:
        - tx: float, translated correction value along x-axis
        - ty: float, translated correction value along y-axis
    '''
    target_x = scale(np.mean(target, axis=0))
    target_y = scale(np.mean(target, axis=1))
    img_x = scale(np.mean(img, axis=0))
    img_y = scale(np.mean(img, axis=1))

    tx = np.mean((np.where(target_x > thresh))) - np.mean((np.where(img_x > thresh)))
    ty = np.mean((np.where(target_y > thresh))) - np.mean((np.where(img_y > thresh)))

    return tx, ty


def translate(img, tx, ty):
    '''
    Transform an img frame based on tx and ty translation values.
    Input:
        - img: numpy array, frame to transform
        - tx: float, translated correction value along x-axis
        - ty: float, translated correction value along y-axis
    Output:
        - numpy array of transformed frame
    '''
    transf = SimilarityTransform(translation=[tx, ty])

    return warp(img, transf)


def spatial_lp_filter(video, order, Wn):
    '''
    Filter the active neurons from image leaving only background.
    Input:
        - video: numpy array, dim(frame, x, y)
        - order: int, how sharp cutoff is for low-pass Filter
        - Wn: float between 0 and 1, angular frequency
    Output:
        - video_filtered: numpy array, dim(frame, x, y) of filtered video
    '''
    b, a = signal.butter(order, Wn, btype='low')
    video_flt = signal.filtfilt(b, a, video, axis=1)
    video_flt = signal.filtfilt(b, a, video_flt, axis=2)
    video_filtered = video_flt/np.amax(np.abs(video_flt))

    return video_filtered
