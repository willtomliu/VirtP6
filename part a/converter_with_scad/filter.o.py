#@ type: compute
#@ parents:
#@   - select
#@ dependents:
#@   - output
#@ corunning:
#@   mem2:
#@     trans: mem2
#@     type: rdma
#@   mem3:
#@     trans: mem3
#@     type: rdma

import cv2
import pickle
import numpy as np
import json
import base64
import disaggrt.buffer_pool_lib as buffer_pool_lib
from disaggrt.rdma_array import remote_array
import urllib.request
from PIL import Image


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


def scale_image(original_image, width=None, height=None):
    w, h = original_image.shape[0], original_image.shape[1]
    if width and height:
        max_size = (width, height)
    elif width:
        max_size = (width, h)
    elif height:
        max_size = (w, height)
    else:
        # No width or height specified
        raise RuntimeError('Width or height required!')
    resized =  cv2.resize(original_image, max_size)
    return resized


def main(params, action):
    filter_context_dict = {}
    # read metadata to setup
    trans2 = action.get_transport('mem2', 'rdma')
    trans2.reg(buffer_pool_lib.buffer_size)

    context_dict_in_b64 = params["select"][0]['meta']
    context_dict_in_byte = base64.b64decode(context_dict_in_b64)
    context_dict = pickle.loads(context_dict_in_byte)
    buffer_pool_select = buffer_pool_lib.buffer_pool({'mem2': trans2})

    trans3 = action.get_transport('mem3', 'rdma')
    trans3.reg(buffer_pool_lib.buffer_size)

    resized_width = context_dict["target_resolution"][0]
    resized_height =  context_dict["target_resolution"][1]
    resized_stride = int(buffer_pool_lib.buffer_size/(resized_height*resized_width*3))
    resized_image_buffer = image_buffer(resized_stride, resized_height, resized_width, trans3, 'mem3')

    for metadata in context_dict["remote_input"]:
        original_images = remote_array(buffer_pool_select, metadata=metadata).materialize()
        print(original_images.shape[0])
        for i in range(original_images.shape[0]):
            resized_image = scale_image(original_images[i], resized_width,resized_height)
            resized_image_buffer.put(resized_image)

    resized_image_buffer.flush()

    filter_context_dict["remote_input"] = resized_image_buffer.remote_input
    filter_context_dict["target_resolution"] = context_dict["target_resolution"]
    filter_context_dict_in_byte = pickle.dumps(filter_context_dict)
    return {'meta': base64.b64encode(filter_context_dict_in_byte).decode("ascii")}