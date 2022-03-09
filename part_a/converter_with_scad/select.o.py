#@ type: compute
#@ parents:
#@   - decode
#@ dependents:
#@   - filter
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
    select_context_dict = {}
    # read metadata to setup
    trans = action.get_transport('mem1', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)
    trans2 = action.get_transport('mem2', 'rdma')
    trans2.reg(buffer_pool_lib.buffer_size)


    context_dict_in_b64 = params["decode"][0]['meta']
    context_dict_in_byte = base64.b64decode(context_dict_in_b64)
    context_dict = pickle.loads(context_dict_in_byte)

    height = context_dict["resolution"][1]
    width = context_dict["resolution"][0]


    buffer = image_buffer(context_dict["buffer_image_num"], height, width, trans2, 'mem2')

    count = 0
    for metadata in context_dict["remote_input"]:
        buffer_pool = buffer_pool_lib.buffer_pool({'mem1': trans})
        images = remote_array(buffer_pool, metadata=metadata).materialize()
        for i in range(images.shape[0]):
            if count%10 == 0:
                buffer.put(images[i])
            count += 1
    buffer.flush()

    select_context_dict["remote_input"] = buffer.remote_input
    select_context_dict["target_resolution"] = context_dict["target_resolution"]
    select_context_dict["buffer_image_num"] = context_dict["buffer_image_num"]
    select_context_dict_in_byte = pickle.dumps(select_context_dict)
    return {'meta': base64.b64encode(select_context_dict_in_byte).decode("ascii")}
