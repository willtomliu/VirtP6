#@ type: compute
#@ parents:
#@   - select
#@ dependents:
#@   - output
#@ corunning:
#@   mem1:
#@     trans: mem1
#@     type: rdma
#@   mem2:
#@     trans: mem2
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
    trans = action.get_transport('mem1', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)

    context_dict_in_b64 = params["select"][0]['meta']
    context_dict_in_byte = base64.b64decode(context_dict_in_b64)
    context_dict = pickle.loads(context_dict_in_byte)
    buffer_pool_select = buffer_pool_lib.buffer_pool({'mem1': trans}, context_dict["buffer_pool_metadata"])

    trans2 = action.get_transport('mem2', 'rdma')
    trans2.reg(buffer_pool_lib.buffer_size, trans)
    buffer_pool = buffer_pool_lib.buffer_pool({'mem2': trans2})

    filter_context_dict["select_index"] = context_dict["select_index"]

    for metadata in context_dict["remote_input"]:
        original_images = remote_array(buffer_pool_select, metadata=metadata).materialize()
        resized_images = np.empty(
            (len(context_dict["select_index"]), 200, 100, 3), dtype=np.uint8)
        resized_count = 0
        for i in context_dict["select_index"]:
            resized_images[resized_count] = scale_image(original_images[i], 100,200)
            resized_count+=1
        remote_input = remote_array(buffer_pool, input_ndarray=resized_images, transport_name='mem2')
        filter_context_dict["remote_input"] = remote_input.get_array_metadata()

    filter_context_dict["buffer_pool_metadata"] = buffer_pool.get_buffer_metadata()






    filter_context_dict_in_byte = pickle.dumps(filter_context_dict)
    return {'meta': base64.b64encode(filter_context_dict_in_byte).decode("ascii")}