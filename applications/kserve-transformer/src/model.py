import logging
import io
import base64
import re
import argparse
import numpy as np

from kserve import Model, ModelServer, model_server, InferInput, InferRequest, InferResponse
from typing import Dict, Union
from PIL import Image

logging.basicConfig(level="DEBUG")

def image_transform(img_string):
    """converts the input image of Bytes Array into Tensor
    Args:
        instance (dict): The request input for image bytes.
    Returns:
        list: Returns converted tensor as input for predict handler with v1/v2 inference protocol.
    """
    img_str = re.search(r'base64,(.*)', img_string).group(1)
    image_bytes = io.BytesIO(base64.b64decode(img_str))
    im = Image.open(image_bytes)
    arr = np.array(im)[:,:,0:1]
    arr = (255 - arr) / 255
    res = arr.reshape(28, 28, 1)
    return res

# for v1 REST predictor the preprocess handler converts to input image bytes to float tensor dict in v1 inference REST protocol format
class ImageTransformer(Model):
    def __init__(self, name: str, predictor_host: str, protocol: str, use_ssl: bool):
        super().__init__(name)
        self.predictor_host = predictor_host
        self.protocol = protocol
        self.use_ssl = use_ssl
        self.ready = True
    
    def preprocess(self, payload: Dict, headers: Dict[str, str] = None) -> Dict:
        input_tensors = [image_transform(instance) for instance in payload.inputs[0].data]
        input_tensors = np.asarray(input_tensors, dtype=np.float32)
        infer_inputs = [InferInput(name="input_1", datatype='FP32', shape=list(input_tensors.shape),
                                   data=input_tensors)]
        infer_request = InferRequest(model_name=self.name, infer_inputs=infer_inputs)
        # #inputs = [{"data": input_tensor.tolist()} for input_tensor in input_tensors]
        # inputs = [{"data": [np.array2string(input_tensors)]}]
        # print(inputs)
        # inputs[0]["datatype"]="FP32"
        # inputs[0]["name"]="input_1"
        # inputs[0]["shape"]=list(input_tensors.shape)
        # payload = {"inputs": inputs}
        # print(payload)
        # return payload
        return infer_request

    def postprocess(self, infer_response: Dict, headers: Dict[str, str] = None) -> Dict:
        return infer_response
    
parser = argparse.ArgumentParser(parents=[model_server.parser])
args, _ = parser.parse_known_args()
print(args)


if __name__ == "__main__":
    print(args)
    model = ImageTransformer(args.model_name, predictor_host=args.predictor_host,
                             protocol=args.protocol, use_ssl=args.predictor_use_ssl)
    ModelServer().start([model])