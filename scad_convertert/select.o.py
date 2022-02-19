#@ type: compute
#@ parents:
#@   - decode
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
    # TODO: Read and select results from memory elements

    # TODO: Output results to another memory elements

    # read metadata to setup
    trans = action.get_transport('mem1', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)
    context_dict_in_b64 = params["decode"][0]['meta']
    context_dict_in_byte = base64.b64decode(context_dict_in_b64)
    context_dict = pickle.loads(context_dict_in_byte)
    buffer_pool = buffer_pool_lib.buffer_pool({'mem1': trans}, context_dict["buffer_pool_metadata"])

    # image = remote_array(buffer_pool, metadata=context_dict["remote_input"]).materialize()
    counter = 0
    for metadata in context_dict["remote_input"]:
        print(metadata)
        images = remote_array(buffer_pool, metadata=metadata).materialize()
        for i in range(images.shape[0]):
            cv2.imwrite("output/output"+str(counter)+".jpg", images[i])
            counter = counter+1
    return {}
