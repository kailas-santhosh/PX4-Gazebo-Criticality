#!/usr/bin/env python3

"""
Image degradation utilities.

This module contains pure OpenCV image processing functions.

No ROS code should exist here.

Every function:

    image -> degraded image

This keeps the camera degradation pipeline modular and easily extensible.
"""

import random

import cv2
import numpy as np


# --------------------------------------------------
# Gaussian Noise
# --------------------------------------------------

def add_gaussian_noise(image, level):
    """
    Add Gaussian noise.

    Parameters
    ----------
    image : np.ndarray
    level : float
        Noise strength in [0,1]
    """

    sigma = max(level, 0.0) * 255.0

    noise = np.random.normal(
        0,
        sigma,
        image.shape,
    )

    noisy = image.astype(np.float32) + noise

    noisy = np.clip(
        noisy,
        0,
        255,
    )

    return noisy.astype(np.uint8)


# --------------------------------------------------
# Motion Blur
# --------------------------------------------------

def add_motion_blur(
    image,
    kernel_size=15,
):
    """
    Horizontal motion blur.
    """

    kernel_size = max(
        3,
        int(kernel_size),
    )

    if kernel_size % 2 == 0:
        kernel_size += 1

    kernel = np.zeros(
        (
            kernel_size,
            kernel_size,
        ),
        dtype=np.float32,
    )

    kernel[
        kernel_size // 2,
        :
    ] = 1.0

    kernel /= kernel_size

    return cv2.filter2D(
        image,
        -1,
        kernel,
    )


# --------------------------------------------------
# Gaussian Blur
# --------------------------------------------------

def add_blur(
    image,
    kernel_size=7,
):
    """
    Standard Gaussian blur.
    """

    kernel_size = max(
        3,
        int(kernel_size),
    )

    if kernel_size % 2 == 0:
        kernel_size += 1

    return cv2.GaussianBlur(
        image,
        (
            kernel_size,
            kernel_size,
        ),
        0,
    )


# --------------------------------------------------
# Brightness
# --------------------------------------------------

def adjust_brightness(
    image,
    factor,
):
    """
    factor > 1.0 brighter

    factor < 1.0 darker
    """

    img = image.astype(np.float32)

    img *= factor

    img = np.clip(
        img,
        0,
        255,
    )

    return img.astype(np.uint8)


# --------------------------------------------------
# Contrast
# --------------------------------------------------

def adjust_contrast(
    image,
    factor,
):
    """
    Adjust image contrast.
    """

    img = image.astype(np.float32)

    img = (img - 127.5) * factor + 127.5

    img = np.clip(
        img,
        0,
        255,
    )

    return img.astype(np.uint8)


# --------------------------------------------------
# Salt & Pepper Noise
# --------------------------------------------------

def add_salt_pepper_noise(
    image,
    probability=0.02,
):
    """
    Random salt & pepper noise.
    """

    output = image.copy()

    rows, cols = output.shape[:2]

    total = int(
        probability * rows * cols
    )

    #
    # Salt
    #

    for _ in range(total // 2):

        y = random.randint(
            0,
            rows - 1,
        )

        x = random.randint(
            0,
            cols - 1,
        )

        output[
            y,
            x,
        ] = 255

    #
    # Pepper
    #

    for _ in range(total // 2):

        y = random.randint(
            0,
            rows - 1,
        )

        x = random.randint(
            0,
            cols - 1,
        )

        output[
            y,
            x,
        ] = 0

    return output


# --------------------------------------------------
# Frame Drop
# --------------------------------------------------

def drop_frame(
    image,
):
    """
    Simulate a dropped frame.

    Returning None allows the caller to skip
    publishing this frame.
    """

    return None


# --------------------------------------------------
# Identity
# --------------------------------------------------

def identity(
    image,
):
    """
    Return the original image.
    """

    return image
