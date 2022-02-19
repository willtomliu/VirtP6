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

def main(params, action):
    path = "demo.mp4"
    video_capture = cv2.VideoCapture(path)
    still_reading, image = video_capture.read()

    # setup
    trans = action.get_transport('mem1', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)
    buffer_pool = buffer_pool_lib.buffer_pool({'mem1':trans})

    # loading data
    remote_input = remote_array(buffer_pool, input_ndarray=image, transport_name='mem1')


    # update context
    remote_input_metadata = remote_input.get_array_metadata()
    context_dict = {}
    context_dict["remote_input"] = remote_input_metadata
    context_dict["buffer_pool_metadata"] = buffer_pool.get_buffer_metadata()

    context_dict_in_byte = pickle.dumps(context_dict)
    return {'meta': base64.b64encode(context_dict_in_byte).decode("ascii")}


    # frame_count = 0
    # while still_reading:
    #
    #     # cv2.imwrite(f"output/frame_{frame_count:03d}.jpg", image)
    #     # TODO: Save results to memory elements
    #     # read next image
    #     still_reading, image = video_capture.read()
    #     frame_count += 1