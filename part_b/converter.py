import gc

import cv2
import os
from PIL import Image


@profile
def decode(resourcePath):
    video_capture = cv2.VideoCapture(resourcePath)
    still_reading = True
    all_images = []

    while still_reading:
        still_reading, image = video_capture.read()
        all_images.append(image)
    gc.collect()
    return all_images


@profile
def select(all_images):
    selected_images = []
    skip = 10
    for index, image in enumerate(all_images):
        if index % skip == 0:
            selected_images.append(image.copy())
    gc.collect()
    return selected_images


@profile
def filter(selected_images):
    filtered_images = []
    width, height = 200, 100
    first_image = selected_images[0]
    w, h, _ = first_image.shape
    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        raise RuntimeError('Width or height required!')

    for count, image in enumerate(selected_images):
        filtered_images.append(cv2.resize(image, max_size))
    gc.collect()
    return filtered_images


@profile
def output(outputPath, filtered_images):
    frames = [Image.fromarray(image) for image in filtered_images]
    frame_one = frames[0]
    frame_one.save(outputPath, format="GIF", append_images=frames, save_all=True, duration=50, loop=0)
    gc.collect()



# @profile
def main():
    # Settings
    resourceFolder = "../part_a/converter_with_scad"
    resourceName = "bigger"
    resourceType = "mp4"
    resourcePath = os.path.join(resourceFolder,
                                f"{resourceName}.{resourceType}")

    outputFolder = "."
    outputName = resourceName
    outputType = "gif"
    outputPath = os.path.join(outputFolder, f"{outputName}.{outputType}")

    x = decode(resourcePath)
    x = select(x)
    x = filter(x)
    output(outputPath, x)


if __name__ == '__main__':
    main()
