import glob
from PIL import Image


def make_gif(frame_folder):
    images = glob.glob(f"{frame_folder}/*.jpg")
    images.sort()
    frames = [Image.open(image) for image in images]
    frame_one = frames[0]
    frame_one.save("flask_demo.gif", format="GIF", append_images=frames,
                   save_all=True, duration=50, loop=0)


if __name__ == "__main__":
    make_gif("output")