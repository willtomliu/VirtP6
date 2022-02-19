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
    # setup
    trans = action.get_transport('mem1', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)
    buffer_pool = buffer_pool_lib.buffer_pool({'mem1': trans})
    context_dict = {}
    context_dict["remote_input"] = []
    path = "demo.mp4"
    debug_count = 0

    stride = 200
    video_capture = cv2.VideoCapture(path)
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    still_reading = True
    save_frame_list = []
    # save_frame = np.empty((stride, height, width, 3), dtype=np.uint8)
    while still_reading:
        save_frame_list.append(np.empty((stride, height, width, 3), dtype=np.uint8))
        save_frame = save_frame_list[-1]
        for i in range(0, stride):
            still_reading, image = video_capture.read()
            if still_reading:
                save_frame[i] = image
            else:
                if i == 0:
                    break
                else:
                    # uploading data
                    print("bjnb")
                    remote_input = remote_array(buffer_pool, input_ndarray=save_frame[:i], transport_name='mem1')
                    # update context
                    remote_input_metadata = remote_input.get_array_metadata()
                    context_dict["remote_input"].append(remote_input_metadata)
                    break
        if still_reading:
            # uploading data
            print(debug_count)
            debug_count+=1
            remote_input = remote_array(buffer_pool, input_ndarray=save_frame, transport_name='mem1')
            # print(save_frame)
            # update context
            remote_input_metadata = remote_input.get_array_metadata()
            context_dict["remote_input"].append(remote_input_metadata)
            if debug_count == 1:
                break



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