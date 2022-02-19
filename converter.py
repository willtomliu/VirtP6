import cv2
import glob
import os
import shutil

from PIL import Image

def convert_mp4_to_jpgs(path):
    video_capture = cv2.VideoCapture(path)
    still_reading, image = video_capture.read()
    frame_count = 0

    if os.path.exists("output"):
        shutil.rmtree("output")
    try:
        os.mkdir("output")
    except IOError:
        print("Error occurred creating output folder")
        return

    while still_reading:
        cv2.imwrite(f"output/frame_{frame_count:04d}.jpg", image)
        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1

def scale_image(frame_folder, width=None, height=None):
    images = glob.glob(f"{frame_folder}/*.jpg")
    images.sort()
    if not images:
        raise RuntimeError("jpg files required!")
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
    for image in images:
        img = Image.open(image)
        img.thumbnail(max_size, Image.ANTIALIAS)
        prefix, suffix = image.split('.')
        output_image_path = '.'.join([prefix + '_resized', suffix])
        img.save(output_image_path)
        img.close()


def make_gif(frame_folder, filename):
    images = glob.glob(f"{frame_folder}/*_resized.jpg")
    images.sort()
    if not images:
        raise RuntimeError("jpg files required!")
    frames = [Image.open(image) for image in images]
    frame_one = frames[0]
    frame_one.save(filename, format="GIF", append_images=frames,
                   save_all=True, duration=50, loop=0)

name = "flask_demo"
mp4_path = f"{name}.mp4"
frame_folder = "output"
filename = f"{name}.gif"
convert_mp4_to_jpgs(mp4_path)
scale_image(frame_folder, 800)
make_gif(frame_folder, filename)

