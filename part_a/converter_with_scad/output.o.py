#@ type: compute
#@ parents:
#@   - filter
#@ corunning:
#@   mem3:
#@     trans: mem3
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
    trans3 = action.get_transport('mem3', 'rdma')
    trans3.reg(buffer_pool_lib.buffer_size)

    context_dict_in_b64 = params["filter"][0]['meta']
    context_dict_in_byte = base64.b64decode(context_dict_in_b64)
    context_dict = pickle.loads(context_dict_in_byte)

    frames = np.empty((0, context_dict["target_resolution"][1], context_dict["target_resolution"][0], 3), dtype=np.uint8)
    for metadata in context_dict["remote_input"]:
        buffer_pool = buffer_pool_lib.buffer_pool({'mem3': trans3})
        resized_images = remote_array(buffer_pool, metadata=metadata).materialize()
        frames = np.concatenate((frames, resized_images), axis=0)

    output_frames = [Image.fromarray(img) for img in frames]
    output_frames[0].save("demo.gif", format="GIF", append_images=output_frames[1:],
                   save_all=True, duration=50, loop=0)

    return {}
