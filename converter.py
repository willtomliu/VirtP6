import cv2
import glob
import os
import shutil

def convert_mp4_to_jpgs(path):
    video_capture = cv2.VideoCapture(path)
    still_reading, image = video_capture.read()
    frame_count = 0
    count = 0
    while still_reading:
        count = count+1
        cv2.imwrite(f"output/frame_{frame_count:03d}.jpg", image)

        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1

def make_gif(frame_folder):
    images = glob.glob(f"{frame_folder}/*.jpg")
    images.sort()
    frames = [Image.open(image) for image in images]
    frame_one = frames[0]
    frame_one.save("flask_demo.gif", format="GIF", append_images=frames,
                   save_all=True, duration=50, loop=0)


mp4_path = "flask_demo.mp4"
gif_path = "output"
convert_mp4_to_jpgs(mp4_path)
resize(sdsd)
make_gif(gif_path)

