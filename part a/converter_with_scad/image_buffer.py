import numpy as np
import disaggrt.buffer_pool_lib as buffer_pool_lib
from disaggrt.rdma_array import remote_array


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