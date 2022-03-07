import cv2


def convert_mp4_to_jpgs(path):
    video_capture = cv2.VideoCapture(path)
    still_reading, image = video_capture.read()
    frame_count = 0
    n = 0
    while still_reading:
        n += 1
        print(n)
        print(cv2.imwrite(f"output/frame_{frame_count:03d}.jpg", image))

        # read next image
        still_reading, image = video_capture.read()
        frame_count += 1


if __name__ == "__main__":
    convert_mp4_to_jpgs("flask_demo.mp4")