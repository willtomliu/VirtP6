#@ type: compute
#@ parents:
#@   - filter
#@ corunning:
#@   mem2:
#@     trans: mem2
#@     type: rdma

from PIL import Image
import cv2
import pickle
import numpy as np
import json
import base64
import disaggrt.buffer_pool_lib as buffer_pool_lib
from disaggrt.rdma_array import remote_array
def main(params, action):
    filter_context_dict = {}
    # read metadata to setup
    trans = action.get_transport('mem2', 'rdma')
    trans.reg(buffer_pool_lib.buffer_size)

    context_dict_in_b64 = params["filter"][0]['meta']
    context_dict_in_byte = base64.b64decode(context_dict_in_b64)
    context_dict = pickle.loads(context_dict_in_byte)
    buffer_pool = buffer_pool_lib.buffer_pool({'mem2': trans}, context_dict["buffer_pool_metadata"])

    resized_images = remote_array(buffer_pool, metadata=context_dict["remote_input"]).materialize()
    frames = [Image.fromarray(img) for img in resized_images]
    frames[0].save("flask_demo.gif", format="GIF", append_images=frames[1:],
                   save_all=True, duration=50, loop=0)

    return {}
