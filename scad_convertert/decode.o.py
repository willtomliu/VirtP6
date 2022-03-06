#@ type: compute
#@ dependents:
#@   - select
#@ corunning:
#@   mem1:
#@     trans: mem1
#@     type: rdma

import cv2
import pickle
import numpy as np
import json
import base64
import disaggrt.buffer_pool_lib as buffer_pool_lib
from disaggrt.rdma_array import remote_array
import urllib.request

class image_buffer:
    def __init__(self, max_image_num, height, width, trans, memory_name, buffer_context = {}):
        self.trans = trans
        self.memory_name = memory_name
        self.max_image_num = max_image_num
        self.current_image_num = 0
        self.buffer = np.empty((max_image_num, height, width, 3), dtype=np.uint8)
        self.buffer_context = buffer_context
        self.remote_input = []

    def put(self, image):
        self.buffer[self.current_image_num] = image
        self.current_image_num += 1
        if self.current_image_num == self.max_image_num:
            self.flush()

    def flush(self):
        if self.current_image_num != 0:
            buffer_pool = buffer_pool_lib.buffer_pool({self.memory_name: self.trans}, self.buffer_context)
            remote_input = remote_array(buffer_pool, input_ndarray=self.buffer[:self.current_image_num],
                                        transport_name=self.memory_name)
            self.buffer_context = buffer_pool.get_buffer_metadata()
            remote_input_metadata = remote_input.get_array_metadata()
            self.remote_input.append(remote_input_metadata)
            self.current_image_num = 0



def main(params, action):
    resized_width = 200
    resized_height = 100
    # setup
    trans = action.get_transport('mem1', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)
    context_dict = {}
    path = "demo.mp4"
    debug_count = 0

    video_capture = cv2.VideoCapture(path)
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))

    stride = int(buffer_pool_lib.buffer_size/(width*height*3))

    buffer = image_buffer(stride, height, width, trans, 'mem1')
    still_reading = True

    still_reading, image = video_capture.read()
    while still_reading:
        buffer.put(image)
        still_reading, image = video_capture.read()
    buffer.flush()

    context_dict["remote_input"] = buffer.remote_input
    context_dict["resolution"] = [width, height]
    context_dict["target_resolution"] = [resized_width, resized_height]
    context_dict["buffer_image_num"] = stride

    context_dict_in_byte = pickle.dumps(context_dict)
    return {'meta': base64.b64encode(context_dict_in_byte).decode("ascii")}
