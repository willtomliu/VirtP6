import cv2
import glob
import os
import shutil

from PIL import Image


def decode(resourcePath, outFolder):
    video_capture = cv2.VideoCapture(resourcePath)
    still_reading, image = video_capture.read()
    frame_count = 0

    while still_reading:
        cv2.imwrite(f"{outFolder}/frame_{frame_count:04d}.jpg", image)
        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1


# def select(inFolder, outFolder, inType, outType):
#     images = glob.glob(f"{inFolder}/*.{inType}")
#     images.sort()
#     if not images:
#         raise RuntimeError("jpg files required!")
#     skip = 10
#     selectedIndex = []
#     for index, image in enumerate(images):
#         if index % skip == 0:
#             selectedIndex.append(index)
#     return selectedIndex


def select(inFolder, outFolder, inType, outType=None):
    images = glob.glob(f"{inFolder}/*.{inType}")
    images.sort()
    if not images:
        raise RuntimeError("jpg files required!")
    skip = 10
    for index, image in enumerate(images):
        if index % skip == 0:
            _, fileName = os.path.split(image)
            shutil.copy(image, os.path.join(outFolder, fileName))


# def filter(inFolder, outFolder, inType, outType, selectedIndex, width=None,
#            height=None):
#     images = glob.glob(f"{inFolder}/*.{inType}")
#     images.sort()
#     if not images:
#         raise RuntimeError("jpg files required!")
#     first_image = Image.open(images[0])
#     w, h = first_image.size
#     if width and height:
#         max_size = (width, height)
#     elif width:
#         max_size = (width, h)
#     elif height:
#         max_size = (w, height)
#     else:
#         raise RuntimeError('Width or height required!')
#     for count, index in enumerate(selectedIndex):
#         img = Image.open(images[index])
#         img.resize(max_size, Image.ANTIALIAS)
#         outImagePath = os.path.join(outFolder,
#                                     f"frame{count:04d}_resized.{outType}")
#         img.save(outImagePath)
#         img.close()


def filter(inFolder, outFolder, inType, outType, width=None, height=None):
    images = glob.glob(f"{inFolder}/*.{inType}")
    images.sort()
    if not images:
        raise RuntimeError(f"{inType} files required!")
    first_image = Image.open(images[0])
    w, h = first_image.size
    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        raise RuntimeError('Width or height required!')
    for count, image in enumerate(images):
        img = Image.open(image)
        img.resize(max_size, Image.ANTIALIAS)
        outImagePath = os.path.join(outFolder,
                                    f"frame{count:04d}_resized.{outType}")
        img.save(outImagePath)
        img.close()


def output(inFolder, outputPath, inType, outType):
    images = glob.glob(f"{inFolder}/*{inType}")
    images.sort()
    if not images:
        raise RuntimeError(f"{inType} files required!")
    frames = [Image.open(image) for image in images]
    frame_one = frames[0]
    frame_one.save(outputPath, format=outType, append_images=frames,
                   save_all=True, duration=50, loop=0)


def main():
    resourceFolder = "resource"
    resourceName = "flask_demo"
    resourceType = "mp4"
    resourcePath = os.path.join(resourceFolder,
                                f"{resourceName}.{resourceType}")

    mem1 = "mem1"
    mem2 = "mem2"
    mem3 = "mem3"

    outputFolder = "output"
    outputName = resourceName
    outputType = "gif"
    outputPath = os.path.join(outputFolder, f"{outputName}.{outputType}")

    for outDir in [mem1, mem2, mem3, outputFolder]:
        if os.path.exists(outDir):
            shutil.rmtree(outDir)
        try:
            os.mkdir(outDir)
        except IOError:
            print("Error occurred creating output folder")
            return

    decode(resourcePath, mem1)
    select(mem1, mem2, "jpg")
    filter(mem2, mem3, "jpg", "jpg", 800)
    output(mem3, outputPath, "jpg", "GIF")


if __name__ == '__main__':
    main()
